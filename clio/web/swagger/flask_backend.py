import gzip
import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, Type

from flask import Flask
from flask import Request as FlaskRequest
from flask import Response as FlaskResponse
from flask import abort, jsonify, make_response, request
from werkzeug.datastructures import Headers
from werkzeug.routing import Rule, parse_converter_args

from clio.pydantics import BaseModel, Field, ValidationError

from .config import Config
from .page import PAGES
from .types import RequestBase, ResponseBase, ValidateError, ValidateErrorItem
from .utils import parse_multi_dict, parse_rule


class FlaskContext(BaseModel):
    query: Optional[BaseModel] = Field(None, description="query")
    body: Optional[BaseModel] = Field(None, description="body")
    headers: Optional[BaseModel] = Field(None, description="headers")
    cookies: Optional[BaseModel] = Field(None, description="cookies")


class FlaskBackend:
    def __init__(self, validator: Any) -> None:
        self.validator = validator
        self.config: Config = validator.config
        self.logger: logging.Logger = logging.getLogger(__name__)

    def find_routes(self) -> Any:
        for rule in self.app.url_map.iter_rules():
            if any(
                str(rule).startswith(path)
                for path in (f"/{self.config.PATH}", "/static")
            ):
                continue
            yield rule

    def bypass(self, func: Callable, method: str) -> bool:
        if method in ["HEAD", "OPTIONS"]:
            return True
        return False

    def parse_func(self, route: Any) -> Any:
        func = self.app.view_functions[route.endpoint]
        for method in route.methods:
            yield method, func

    def parse_path(self, route: Rule) -> Tuple[str, List[Any]]:
        subs = []
        parameters = []

        for converter, arguments, variable in parse_rule(route):
            if converter is None:
                subs.append(variable)
                continue
            subs.append(f"{{{variable}}}")

            args: Iterable[Any] = []
            kwargs: Dict[str, Any] = {}

            if arguments:
                args, kwargs = parse_converter_args(arguments)

            schema = None
            # See: https://werkzeug.palletsprojects.com/en/2.3.x/routing/#built-in-converters
            if converter == "any":
                schema = {
                    "type": "string",
                    "enum": list(args),
                }
            elif converter == "int":
                schema = {
                    "type": "integer",
                    "format": "int32",
                }
                if "max" in kwargs:
                    schema["maximum"] = kwargs["max"]
                if "min" in kwargs:
                    schema["minimum"] = kwargs["min"]
            elif converter == "float":
                schema = {
                    "type": "number",
                    "format": "float",
                }
            elif converter == "uuid":
                schema = {
                    "type": "string",
                    "format": "uuid",
                }
            elif converter == "path":
                schema = {
                    "type": "string",
                    "format": "path",
                }
            elif converter == "string":
                schema = {
                    "type": "string",
                }
                if "length" in kwargs:
                    schema["length"] = kwargs["length"]
                if "maxlength" in kwargs:
                    schema["maxLength"] = kwargs["maxlength"]
                if "minlength" in kwargs:
                    schema["minLength"] = kwargs["minlength"]
            elif converter == "default":
                schema = {"type": "string"}
            else:
                schema = _parse_custom_url_converter(converter, self.app) or {
                    "type": "string"
                }

            parameters.append(
                {
                    "name": variable,
                    "in": "path",
                    "required": True,
                    "schema": schema,
                }
            )

        return "".join(subs), parameters

    def request_validation(
        self,
        flask_request: FlaskRequest,
        query: Optional[Type[BaseModel]],
        body: Optional[RequestBase],
        headers: Optional[Type[BaseModel]],
        cookies: Optional[Type[BaseModel]],
    ) -> None:
        raw_query = flask_request.args or None
        if raw_query is not None:
            req_query = parse_multi_dict(raw_query)
        else:
            req_query = {}
        if (
            flask_request.content_type
            and "application/json" in flask_request.content_type
        ):
            if (
                flask_request.content_encoding
                and "gzip" in flask_request.content_encoding
            ):
                raw_body = gzip.decompress(flask_request.stream.read()).decode(
                    encoding="utf-8"
                )
                parsed_body = json.loads(raw_body)
            else:
                parsed_body = flask_request.get_json(silent=True) or {}
        elif (
            flask_request.content_type
            and "multipart/form-data" in flask_request.content_type
        ):
            parsed_body = (
                parse_multi_dict(flask_request.form) if flask_request.form else {}
            )
        else:
            parsed_body = flask_request.get_data() or {}
        req_headers: Optional[Headers] = flask_request.headers or None
        req_cookies: Optional[Mapping[str, str]] = flask_request.cookies or None

        # query
        _query = None
        error_list: List[ValidateErrorItem] = []
        if query:
            try:
                _query = query.parse_obj(req_query)
            except ValidationError as e:
                error_list.append(
                    ValidateErrorItem("query", query.__name__, e.errors(), req_query)
                )

        # body
        _body = None
        if body and getattr(body, "model"):
            try:
                _body = getattr(body, "model").parse_obj(parsed_body)
            except ValidationError as e:
                error_list.append(
                    ValidateErrorItem(
                        "body",
                        (getattr(body, "model")).__name__,
                        e.errors(),
                        parsed_body,
                    )
                )

        # headers
        _headers = None
        if headers:
            try:
                _headers = headers.parse_obj(req_headers or {})
            except ValidationError as e:
                error_list.append(
                    ValidateErrorItem(
                        "headers", headers.__name__, e.errors(), req_headers or {}
                    )
                )

        # cookies
        _cookies = None
        if cookies:
            try:
                _cookies = cookies.parse_obj(req_cookies or {})
            except ValidationError as e:
                error_list.append(
                    ValidateErrorItem(
                        "cookies", cookies.__name__, e.errors(), req_cookies or {}
                    )
                )

        if len(error_list) > 0:
            raise ValidateError(error_list)

        setattr(
            flask_request,
            "http_context",
            FlaskContext(query=_query, body=_body, headers=_headers, cookies=_cookies),
        )

    def validate(
        self,
        func: Callable,
        query: Optional[Type[BaseModel]],
        body: Optional[RequestBase],
        headers: Optional[Type[BaseModel]],
        cookies: Optional[Type[BaseModel]],
        resp: Optional[ResponseBase],
        before: Callable,
        after: Callable,
        *args: List[Any],
        **kwargs: Mapping[str, Any],
    ) -> FlaskResponse:
        response, req_validation_error_map, resp_validation_error = None, None, None
        try:
            self.request_validation(request, query, body, headers, cookies)
        except ValidateError as err:
            error_map = {}
            for error in err.errors:
                error_map[error.name] = {
                    "model": error.model_name,
                    "errors": error.errors,
                }
            req_validation_error_map = error_map

            response = make_response(
                jsonify(error_map), self.config.VALIDATION_ERROR_CODE
            )

        before(request, response, req_validation_error_map, None)
        if req_validation_error_map:
            abort(response)  # type: ignore
        response = make_response(func(*args, **kwargs))

        if resp and resp.has_model() and getattr(resp, "validate"):
            model = resp.find_model(response.status_code)
            if model:
                try:
                    model.validate(response.get_json())
                except ValidationError as err:
                    resp_validation_error = err
                    response = make_response(
                        jsonify({"message": "response validation error"}), 500
                    )

        after(request, response, resp_validation_error, None)

        return response

    async def async_validate(
        self,
        func: Callable,
        query: Optional[Type[BaseModel]],
        body: Optional[RequestBase],
        headers: Optional[Type[BaseModel]],
        cookies: Optional[Type[BaseModel]],
        resp: Optional[ResponseBase],
        before: Callable,
        after: Callable,
        *args: List[Any],
        **kwargs: Mapping[str, Any],
    ) -> FlaskResponse:
        response, req_validation_error_map, resp_validation_error = None, None, None
        try:
            self.request_validation(request, query, body, headers, cookies)
        except ValidateError as err:
            error_map = {}
            for error in err.errors:
                error_map[error.name] = {
                    "model": error.model_name,
                    "errors": error.errors,
                }
            req_validation_error_map = error_map

            response = make_response(
                jsonify(error_map), self.config.VALIDATION_ERROR_CODE
            )

        before(request, response, req_validation_error_map, None)
        if req_validation_error_map:
            abort(response)  # type: ignore
        response = make_response(await func(*args, **kwargs))

        if resp and resp.has_model() and getattr(resp, "validate"):
            model = resp.find_model(response.status_code)
            if model:
                try:
                    model.validate(response.get_json())
                except ValidationError as err:
                    resp_validation_error = err
                    response = make_response(
                        jsonify({"message": "response validation error"}), 500
                    )

        after(request, response, resp_validation_error, None)

        return response

    def register_route(self, app: Flask) -> None:
        self.app = app
        from flask import jsonify

        self.app.add_url_rule(
            self.config.spec_url,
            "openapi",
            lambda: jsonify(self.validator.spec),
        )

        for ui in PAGES:
            self.app.add_url_rule(
                f"/{self.config.PATH}/{ui}",
                f"doc_page_{ui}",
                view_func=lambda: PAGES[ui].format(self.config),
            )


def _parse_custom_url_converter(converter: str, app: Flask) -> Optional[Dict[str, Any]]:
    """Attempt derive a schema from a custom URL converter."""
    try:
        converter_cls = app.url_map.converters[converter]
        import inspect

        signature = inspect.signature(converter_cls.to_python)
        return_type = signature.return_annotation
        if issubclass(return_type, Enum):
            return {
                "type": "string",
                "enum": [e.value for e in return_type],
            }
    except (KeyError, AttributeError):
        pass
    return None
