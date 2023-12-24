import inspect
from collections import defaultdict
from copy import deepcopy
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Type, Union

from inflection import camelize
from quart import Quart
from quart import Response as FlaskResponse

from clio.pydantics import BaseModel

from . import Request
from .config import Config
from .constants import OPENAPI_SCHEMA_TEMPLATE
from .flask_backend import FlaskBackend
from .types import RequestBase, ResponseBase
from .utils import (
    default_after_handler,
    default_before_handler,
    parse_comments,
    parse_name,
    parse_params,
    parse_request,
    parse_resp,
)


def _move_schema_reference(reference: str) -> str:
    if "/definitions" in reference:
        return f"#/components/schemas/{reference.split('/definitions/')[-1]}"
    return reference


class FlaskPydanticSpec:
    """
    Interface

    :param str backend_name: choose from ('flask')
    :param backend: a backend that inherit `api_doc.FlaskBackend`
    :param app: backend framework application instance (you can also register to it later)
    :param before: a callback function of the form :meth:`fla.utils.default_before_handler`
        ``func(req, resp, req_validation_error, instance)``
        that will be called after the request validation before the endpoint function
    :param after: a callback function of the form :meth:`spectree.utils.default_after_handler`
        ``func(req, resp, resp_validation_error, instance)``
        that will be called after the response validation
    :param kwargs: update default :class:`spectree.config.Config`
    """

    def __init__(
        self,
        backend_name: str = "base",
        backend: Type[FlaskBackend] = FlaskBackend,
        before: Callable = default_before_handler,
        after: Callable = default_after_handler,
        **kwargs: Any,
    ):
        self.before: Callable = before
        self.after: Callable = after
        self.config = Config(**kwargs)
        self.backend_name = backend_name
        self.backend = backend(self)
        # init
        self.models: Dict[str, Any] = {}

    def register(self, app: Quart, register_router=True) -> None:
        """
        register to backend application

        This will be automatically triggered if the app is passed into the
        init step.
        """
        self.app = app
        if register_router:
            self.backend.register_route(self.app)

    @property
    def spec(self) -> Mapping[str, Any]:
        """
        get the OpenAPI spec
        """
        if not hasattr(self, "_spec"):
            self._spec = self._generate_spec()
        return self._spec

    def bypass(self, func: Callable) -> bool:
        """
        bypass rules for routes (mode defined in config)

        :normal:    collect all the routes that are not decorated by other
                    `SpecTree` instance
        :greedy:    collect all the routes
        :strict:    collect all the routes decorated by this instance
        """
        if self.config.MODE == "greedy":
            return False
        elif self.config.MODE == "strict":
            if getattr(func, "_decorator", None) == self:
                return False
            return True
        else:
            decorator = getattr(func, "_decorator", None)
            if decorator and decorator != self:
                return True
            return False

    @staticmethod
    def is_async_function(func):
        return inspect.isasyncgenfunction(func) or inspect.iscoroutinefunction(func)

    def validate(
        self,
        query: Optional[Type[BaseModel]] = None,
        body: Optional[Union[RequestBase, Type[BaseModel]]] = None,
        headers: Optional[Type[BaseModel]] = None,
        cookies: Optional[Type[BaseModel]] = None,
        resp: Optional[ResponseBase] = None,
        tags: Iterable[str] = (),
        deprecated: bool = False,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ) -> Callable:
        """
        - validate query, body, headers in request
        - validate response body and status code
        - add tags to this API route

        :param query: `pydantic.BaseModel`, query in uri like `?name=value`
        :param body: `spectree.Request`, Request body
        :param headers: `pydantic.BaseModel`, if you have specific headers
        :param cookies: `pydantic.BaseModel`, if you have cookies for this route
        :param resp: `spectree.Response`
        :param tags: a tuple of tags string
        :param deprecated: You can mark specific operations as deprecated to indicate that they
                    should be transitioned out of usage
        :param before: :meth:`spectree.utils.default_before_handler` for specific endpoint
        :param after: :meth:`spectree.utils.default_after_handler` for specific endpoint
        """

        def decorate_validation(func: Callable) -> Callable:
            is_async = FlaskPydanticSpec.is_async_function(func)

            if not is_async:
                raise RuntimeError(
                    "Quart Only support async function for now, please use `async def`"
                )

            @wraps(func)
            async def async_validate(*args: Any, **kwargs: Any) -> FlaskResponse:
                return await self.backend.validate(
                    func,
                    query,
                    body if isinstance(body, RequestBase) else Request(body),
                    headers,
                    cookies,
                    resp,
                    before or self.before,
                    after or self.after,
                    *args,
                    **kwargs,
                )

            validation = async_validate

            # register
            for name, model in zip(
                ("query", "body", "headers", "cookies"), (query, body, headers, cookies)
            ):
                if model is not None:
                    if hasattr(model, "model"):
                        _model = getattr(model, "model", None)
                    else:
                        _model = model
                    if _model:
                        self.models[_model.__name__] = self._get_open_api_schema(
                            _model.schema(ref_template=OPENAPI_SCHEMA_TEMPLATE)
                        )
                    setattr(validation, name, model)

            if resp:
                for model in resp.models:
                    if model:
                        assert not isinstance(model, RequestBase)
                        self.models[model.__name__] = self._get_open_api_schema(
                            model.schema(ref_template=OPENAPI_SCHEMA_TEMPLATE)
                        )
                setattr(validation, "resp", resp)

            if tags:
                setattr(validation, "tags", tags)

            if deprecated:
                setattr(validation, "deprecated", True)

            # register decorator
            setattr(validation, "_decorator", self)
            return validation

        return decorate_validation

    def _generate_spec(self) -> Mapping[str, Any]:
        """
        generate OpenAPI spec according to routes and decorators
        """
        tag_lookup = {tag["name"]: tag for tag in self.config.TAGS}
        routes: Dict[str, Any] = {}
        tags: Dict[str, Any] = {}
        for route in self.backend.find_routes():
            path, parameters = self.backend.parse_path(route)
            routes[path] = routes.get(path, {})
            for method, func in self.backend.parse_func(route):
                if self.backend.bypass(func, method) or self.bypass(func):
                    continue

                name = parse_name(func)
                summary, desc = parse_comments(func)
                func_tags = getattr(func, "tags", ())
                for tag in func_tags:
                    if tag not in tags:
                        tags[tag] = tag_lookup.get(tag, {"name": tag})

                routes[path][method.lower()] = {
                    "summary": summary or f"{name} <{method}>",
                    "operationId": camelize(f"{name}", False),
                    "description": desc or "",
                    "tags": getattr(func, "tags", []),
                    "parameters": parse_params(func, parameters[:], self.models),
                    "responses": parse_resp(func, self.config.VALIDATION_ERROR_CODE),
                }
                if hasattr(func, "deprecated"):
                    routes[path][method.lower()]["deprecated"] = True

                request_body = parse_request(func)
                if request_body:
                    routes[path][method.lower()][
                        "requestBody"
                    ] = self._parse_request_body(request_body)

        spec = {
            "openapi": self.config.OPENAPI_VERSION,
            "info": {
                **self.config.INFO,
                **{
                    "title": self.config.TITLE,
                    "version": self.config.VERSION,
                },
            },
            "tags": list(tags.values()),
            "paths": {**routes},
            "components": {"schemas": {**self._get_model_definitions()}},
        }
        return spec

    def _validate_property(self, property: Mapping[str, Any]) -> Dict[str, Any]:
        allowed_fields = {
            "title",
            "multipleOf",
            "maximum",
            "exclusiveMaximum",
            "minimum",
            "exclusiveMinimum",
            "maxLength",
            "minLength",
            "pattern",
            "maxItems",
            "minItems",
            "uniqueItems",
            "maxProperties",
            "minProperties",
            "required",
            "enum",
            "type",
            "allOf",
            "anyOf",
            "oneOf",
            "not",
            "items",
            "properties",
            "additionalProperties",
            "description",
            "format",
            "default",
            "nullable",
            "discriminator",
            "readOnly",
            "writeOnly",
            "xml",
            "externalDocs",
            "example",
            "deprecated",
            "$ref",
        }
        result: Dict[str, Any] = defaultdict(dict)

        for key, value in property.items():
            for prop, val in value.items():
                if prop in allowed_fields:
                    result[key][prop] = val

        return result

    def _get_open_api_schema(self, schema: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Convert a Pydantic model into an OpenAPI compliant schema object.
        """
        result = {}
        for key, value in schema.items():
            if key == "properties":
                result[key] = self._validate_property(value)
            elif key == "$defs":
                for k, v in value.items():
                    self.models[k] = v
            else:
                result[key] = value

        return result

    def _get_model_definitions(self) -> Dict[str, Any]:
        """
        handle nested models
        """
        definitions: Dict[str, Any] = {}
        for model, schema in self.models.items():
            if model not in definitions.keys():
                definitions[model] = deepcopy(schema)

            if "definitions" in schema:
                for key, value in schema["definitions"].items():
                    definitions[key] = self._get_open_api_schema(value)
                del schema["definitions"]
                if "definitions" in definitions[model]:
                    del definitions[model]["definitions"]

        return definitions

    def _parse_request_body(self, request_body: Mapping[str, Any]) -> Mapping[str, Any]:
        content_types = list(request_body["content"].keys())
        if len(content_types) != 1:
            raise RuntimeError(
                "Cannot currently handle multiple content types for a single request"
            )
        else:
            content_type = content_types[0]
        schema = request_body["content"][content_type]["schema"]
        if "$ref" not in schema.keys():
            # handle inline schema definitions
            return {
                "content": {content_type: {"schema": self._get_open_api_schema(schema)}}
            }
        else:
            return request_body
