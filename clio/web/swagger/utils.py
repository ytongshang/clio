import inspect
import json
import logging
import re
from json import JSONDecodeError
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from werkzeug.datastructures import MultiDict
from werkzeug.routing import Rule

from clio.pydantics import BaseModel

from .types import Request, RequestBase, Response, ValidateError

logger = logging.getLogger(__name__)


def parse_comments(func: Callable) -> Tuple[Optional[str], Optional[str]]:
    """
    parse function comments

    First line of comments will be saved as summary, and the rest
    will be saved as description.
    """
    doc = inspect.getdoc(func)
    if doc is None:
        return None, None
    docs = doc.split("\n", 1)
    if len(docs) == 1:
        return docs[0], None
    return docs[0], docs[1].strip()


def parse_request(func: Callable) -> Mapping[str, Any]:
    """
    Generate spec from body parameter on the view function validation decorator
    """
    if hasattr(func, "body"):
        request_body = getattr(func, "body")
        if isinstance(request_body, RequestBase):
            result: Mapping[str, Any] = request_body.generate_spec()
        elif issubclass(request_body, BaseModel):
            result = Request(request_body).generate_spec()
        else:
            result = {}
        return result
    return {}


def parse_params(
    func: Callable,
    params: List[Mapping[str, Any]],
    models: Mapping[str, Any],
) -> List[Mapping[str, Any]]:
    """
    get spec for (query, headers, cookies)
    """
    if hasattr(func, "query"):
        model_name = getattr(func, "query").__name__
        query = models.get(model_name)
        if query is not None:
            for name, schema in query["properties"].items():
                params.append(
                    {
                        "name": name,
                        "in": "query",
                        "schema": schema,
                        "required": name in query.get("required", []),
                    }
                )

    if hasattr(func, "headers"):
        model_name = getattr(func, "headers").__name__
        headers = models.get(model_name)
        if headers is not None:
            for name, schema in headers["properties"].items():
                params.append(
                    {
                        "name": name,
                        "in": "header",
                        "schema": schema,
                        "required": name in headers.get("required", []),
                    }
                )

    if hasattr(func, "cookies"):
        model_name = getattr(func, "cookies").__name__
        cookies = models.get(model_name)
        if cookies is not None:
            for name, schema in cookies["properties"].items():
                params.append(
                    {
                        "name": name,
                        "in": "cookie",
                        "schema": schema,
                        "required": name in cookies.get("required", []),
                    }
                )

    return params


def parse_resp(func: Callable, code: int) -> Mapping[str, Mapping[str, Any]]:
    """
    get the response spec

    If this function does not have explicit ``resp`` but have other models,
    a ``Validation Error`` will be append to the response spec. Since
    this may be triggered in the validation step.
    """
    responses: Dict[str, Any] = {}
    if hasattr(func, "resp"):
        response = getattr(func, "resp")
        if response:
            responses = response.generate_spec()

    if str(code) not in responses and has_model(func):
        responses[str(code)] = {"description": "Validation Error"}

    return responses


def has_model(func: Callable) -> bool:
    """
    return True if this function have ``pydantic.BaseModel``
    """
    if any(hasattr(func, x) for x in ("query", "json", "headers")):
        return True

    if hasattr(func, "resp") and getattr(func, "resp").has_model():
        return True

    return False


def parse_name(func: Callable) -> str:
    """
    the func can be

        * undecorated functions
        * decorated functions
        * decorated class methods
    """
    return func.__name__


def default_before_handler(
    req: Request,
    resp: Response,
    req_validation_error_map: ValidateError,
    instance: BaseModel,
) -> None:
    """
    default handler called before the endpoint function after the request validation

    :param req: request provided by the web framework
    :param resp: response generated by Flask_Pydantic_Spec that will be returned
        if the validation error is not None
    :param req_validation_error_map: request validation error map
    :param instance: class instance if the endpoint function is a class method
    """
    if req_validation_error_map:
        logger.error(
            f"422 Request Validation Error: {json.dumps(req_validation_error_map, indent=2, ensure_ascii=False)}"
        )


def default_after_handler(
    req: Request, resp: Response, resp_validation_error: Any, instance: BaseModel
) -> None:
    """
    default handler called after the response validation

    :param req: request provided by the web framework
    :param resp: response from the endpoint function (if there is no validation error)
        or response validation error
    :param resp_validation_error: response validation error
    :param instance: class instance if the endpoint function is a class method
    """
    if resp_validation_error:
        logger.error(
            f"500 Response Validation Error: {json.dumps(resp_validation_error, indent=2, ensure_ascii=False)}"
        )


def parse_multi_dict(input: MultiDict) -> Dict[str, Any]:
    result = {}
    for key, value in input.to_dict(flat=False).items():
        if len(value) == 1:
            try:
                value_to_use = json.loads(value[0])
            except (TypeError, JSONDecodeError):
                value_to_use = value[0]
        else:
            value_to_use = value
        result[key] = value_to_use
    return result


RE_PARSE_RULE = re.compile(
    r"""
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
    """,
    re.VERBOSE,
)


def parse_rule(rule: Rule) -> Iterable[Tuple[Optional[str], Optional[str], str]]:
    """
    Parse a rule and return it as generator. Each iteration yields tuples in the form
    ``(converter, arguments, variable)``.
    If the converter is `None` it's a static url part, otherwise it's a dynamic one.
    Note: This originally lived in werkzeug.routing.parse_rule until it was
    removed in werkzeug 2.2.0.
    TODO - cgearing - do we really need this?
    """
    rule_str = str(rule)
    pos = 0
    end = len(rule_str)
    do_match = RE_PARSE_RULE.match
    used_names = set()
    while pos < end:
        m = do_match(rule_str, pos)
        if m is None:
            break
        data = m.groupdict()
        if data["static"]:
            yield None, None, data["static"]
        variable = data["variable"]
        converter = data["converter"] or "default"
        if variable in used_names:
            raise ValueError(f"variable name {variable!r} used twice.")
        used_names.add(variable)
        yield converter, data["args"] or None, variable
        pos = m.end()
    if pos < end:
        remaining = rule_str[pos:]
        if ">" in remaining or "<" in remaining:
            raise ValueError(f"malformed url rule: {rule_str!r}")
        yield None, None, remaining
