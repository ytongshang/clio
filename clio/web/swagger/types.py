import re
from typing import Any, Dict, Iterable, Mapping, NamedTuple, Optional, Type

from clio.pydantics import BaseModel

from .constants import OPENAPI_SCHEMA_TEMPLATE


class ResponseBase:
    """
    Base Class for Response Types
    """

    def has_model(self) -> bool:
        raise NotImplementedError

    def find_model(self, code: int) -> Optional[Type[BaseModel]]:
        raise NotImplementedError

    @property
    def models(self) -> Iterable[Type[BaseModel]]:
        raise NotImplementedError

    def generate_spec(self) -> Mapping[str, Any]:
        raise NotImplementedError


class ResponseModel(NamedTuple):
    model: Type[BaseModel]
    is_list: bool = False


class Response(ResponseBase):
    """
    response object

    :param args: list of HTTP status code, format('HTTP_[0-9]{3}'), 'HTTP200'
    :param kwargs: dict of <HTTP status code>: <`pydantic.BaseModel`> or None
    You can also pass `validate` into the kwargs to disable output validation of this model
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self.validate = True
        self.codes = []
        for item in args:
            assert item in DEFAULT_CODE_DESC, "invalid HTTP status code"
            self.codes.append(item)

        self.code_models: Dict[str, ResponseModel] = {}
        for key, value in kwargs.items():
            if key.lower() == "validate":
                assert isinstance(value, bool)
                self.validate = value
            else:
                assert key in DEFAULT_CODE_DESC, "invalid HTTP status code"
                if value:
                    if self.is_list_type(value):
                        assert issubclass(
                            value.__args__[0], BaseModel
                        ), "invalid `pydantic.BaseModel`"
                        self.code_models[key] = ResponseModel(value.__args__[0], True)
                    else:
                        assert issubclass(
                            value, BaseModel
                        ), "invalid `pydantic.BaseModel`"
                        self.code_models[key] = ResponseModel(value, False)
                else:
                    self.codes.append(key)

    @staticmethod
    def is_list_type(value: Any) -> bool:
        return hasattr(value, "__origin__") and value.__origin__ is list

    def has_model(self) -> bool:
        """
        :returns: boolean -- does this response has models or not
        """
        return True if self.code_models else False

    def find_model(self, code: int) -> Optional[Type[BaseModel]]:
        """
        :param code: ``r'\\d{3}'``
        """
        response_model = self.code_models.get(f"HTTP_{code}")
        if response_model:
            return response_model.model
        return None

    @property
    def models(self) -> Iterable[Type[BaseModel]]:
        """
        :returns:  dict_values -- all the models in this response
        """
        return [i.model for i in self.code_models.values()]

    def generate_spec(self) -> Dict[str, Any]:
        """
        generate the spec for responses

        :returns: JSON
        """
        responses: Dict[str, Any] = {}
        for code in self.codes:
            response_code = _parse_code(code)
            if response_code:
                responses[response_code] = {"description": DEFAULT_CODE_DESC[code]}

        for code, response_model in self.code_models.items():
            response_code = _parse_code(code)
            if response_code:
                schema = self.get_schema(
                    response_model.model, is_list=response_model.is_list
                )
                responses[response_code] = {
                    "description": DEFAULT_CODE_DESC[code],
                    "content": {"application/json": schema},
                }

        return responses

    @staticmethod
    def get_schema(model: Type[BaseModel], is_list: bool = False) -> Mapping[str, Any]:
        ref_schema = {"$ref": f"#/components/schemas/{model.__name__}"}
        if is_list:
            return {"schema": {"type": "array", "items": ref_schema}}
        return {"schema": ref_schema}


class FileResponse(ResponseBase):
    def __init__(self, content_type: str = "application/octet-stream"):
        self.content_type = content_type

    def has_model(self) -> bool:
        """
        File response cannot have a model
        """
        return False

    @property
    def models(self) -> Iterable[Type[BaseModel]]:
        return []

    def generate_spec(self) -> Mapping[str, Any]:
        responses = {
            "200": {
                "description": DEFAULT_CODE_DESC["HTTP_200"],
                "content": {
                    self.content_type: {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            "404": {"description": DEFAULT_CODE_DESC["HTTP_404"]},
        }

        return responses


class RequestBase:
    def has_model(self) -> bool:
        raise NotImplementedError

    def generate_spec(self) -> Mapping[str, Any]:
        raise NotImplementedError


class Request(RequestBase):
    def __init__(
        self,
        model: Optional[Type[BaseModel]] = None,
        content_type: str = "application/json",
        encoding: str = "binary",
    ) -> None:
        self.content_type = content_type
        self.model = model
        self.encoding = encoding

    def has_model(self) -> bool:
        return self.model is not None

    def generate_spec(self) -> Mapping[str, Any]:
        if self.content_type == "application/octet-stream":
            return {
                "content": {
                    self.content_type: {
                        "schema": {"type": "string", "format": self.encoding}
                    }
                }
            }
        else:
            assert self.model is not None
            return {
                "content": {
                    self.content_type: {
                        "schema": {
                            "$ref": f"#/components/schemas/{self.model.__name__}"
                        }
                    }
                }
            }


class MultipartFormRequest(RequestBase):
    def __init__(
        self,
        model: Optional[Type[BaseModel]] = None,
        file_key: str = "file",
        encoding: str = "binary",
    ):
        self.content_type = "multipart/form-data"
        self.model = model
        self.file_key = file_key
        self.encoding = encoding

    def has_model(self) -> bool:
        return self.model is not None

    def generate_spec(self) -> Mapping[str, Any]:
        model_spec = (
            self.model.schema(ref_template=OPENAPI_SCHEMA_TEMPLATE)
            if self.model
            else None
        )
        if model_spec:
            additional_properties = model_spec["properties"]
        else:
            additional_properties = {}

        return {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            **additional_properties,
                            self.file_key: {
                                "type": "string",
                                "format": self.encoding,
                            },
                        },
                    }
                }
            }
        }


HTTP_CODE = re.compile(r"^HTTP_(?P<code>\d{3})$")


def _parse_code(http_code: str) -> Optional[str]:
    """
    get the code of this HTTP status

    :param str http_code: format like ``HTTP_200``
    """
    match = HTTP_CODE.match(http_code)
    if not match:
        return None
    return match.group("code")


# according to https://tools.ietf.org/html/rfc2616#section-10
# https://tools.ietf.org/html/rfc7231#section-6.1
# https://developer.mozilla.org/sv-SE/docs/Web/HTTP/Status
DEFAULT_CODE_DESC = {
    # Information 1xx
    "HTTP_100": "Continue",
    "HTTP_101": "Switching Protocols",
    # Successful 2xx
    "HTTP_200": "OK",
    "HTTP_201": "Created",
    "HTTP_202": "Accepted",
    "HTTP_203": "Non-Authoritative Information",
    "HTTP_204": "No Content",
    "HTTP_205": "Reset Content",
    "HTTP_206": "Partial Content",
    # Redirection 3xx
    "HTTP_300": "Multiple Choices",
    "HTTP_301": "Moved Permanently",
    "HTTP_302": "Found",
    "HTTP_303": "See Other",
    "HTTP_304": "Not Modified",
    "HTTP_305": "Use Proxy",
    "HTTP_306": "(Unused)",
    "HTTP_307": "Temporary Redirect",
    "HTTP_308": "Permanent Redirect",
    # Client Error 4xx
    "HTTP_400": "Bad Request",
    "HTTP_401": "Unauthorized",
    "HTTP_402": "Payment Required",
    "HTTP_403": "Forbidden",
    "HTTP_404": "Not Found",
    "HTTP_405": "Method Not Allowed",
    "HTTP_406": "Not Acceptable",
    "HTTP_407": "Proxy Authentication Required",
    "HTTP_408": "Request Timeout",
    "HTTP_409": "Conflict",
    "HTTP_410": "Gone",
    "HTTP_411": "Length Required",
    "HTTP_412": "Precondition Failed",
    "HTTP_413": "Request Entity Too Large",
    "HTTP_414": "Request-URI Too Long",
    "HTTP_415": "Unsupported Media Type",
    "HTTP_416": "Requested Range Not Satisfiable",
    "HTTP_417": "Expectation Failed",
    "HTTP_418": "I'm a teapot",
    "HTTP_421": "Misdirected Request",
    "HTTP_422": "Unprocessable Entity",
    "HTTP_423": "Locked",
    "HTTP_424": "Failed Dependency",
    "HTTP_425": "Too Early",
    "HTTP_426": "Upgrade Required",
    "HTTP_428": "Precondition Required",
    "HTTP_429": "Too Many Requests",
    "HTTP_431": "Request Header Fields Too Large",
    "HTTP_451": "Unavailable For Legal Reasons",
    # Server Error 5xx
    "HTTP_500": "Internal Server Error",
    "HTTP_501": "Not Implemented",
    "HTTP_502": "Bad Gateway",
    "HTTP_503": "Service Unavailable",
    "HTTP_504": "Gateway Timeout",
    "HTTP_505": "HTTP Version Not Supported",
    "HTTP_506": "Variant Also negotiates",
    "HTTP_507": "Insufficient Sotrage",
    "HTTP_508": "Loop Detected",
    "HTTP_511": "Network Authentication Required",
}
