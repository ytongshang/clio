import logging
from typing import Any, Dict, List, Mapping, Optional, Set


class Config:
    """
    :ivar MODE: mode for route. **normal** includes undecorated routes and
        routes decorated by this instance. **strict** only includes routes
        decorated by this instance. **greedy** includes all the routes.
    :ivar PATH: path for API document page
    :ivar OPENAPI_VERSION: OpenAPI version
    :ivar TITLE: service name
    :ivar VERSION: service version
    :ivar DOMAIN: service host domain
    :ivar VALIDATION_ERROR_CODE: code for validation error responses
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.PATH: str = "apidoc"
        self.FILENAME: str = "openapi.json"
        self.OPENAPI_VERSION: str = "3.0.3"
        self.UI: str = "redoc"
        self._SUPPORT_UI: Set[str] = {"redoc", "swagger"}
        self.MODE: str = "normal"
        self._SUPPORT_MODE: Set[str] = {"normal", "strict", "greedy"}
        self.VALIDATION_ERROR_CODE: int = 422

        self.TITLE: str = "Service API Document"
        self.VERSION: str = "0.1"
        self.DOMAIN: Optional[str] = None

        self.INFO: Dict[str, str] = {}
        self.TAGS: List[Mapping[str, str]] = []

        self.logger = logging.getLogger(__name__)

        self.update(**kwargs)

    @property
    def spec_url(self) -> str:
        return f"/{self.PATH}/{self.FILENAME}"

    def __repr__(self) -> str:
        display = "\n{:=^80}\n".format(self.__class__.__name__)
        for k, v in vars(self).items():
            if not k.startswith("__"):
                display += "| {:<30} {}\n".format(k, v)

        return display + "=" * 80

    def update(self, **kwargs: Mapping[str, Any]) -> None:
        """
        update config from key-value pairs

        :param kwargs: key(case insensitive)-value pairs for config

        If the key is not in attributes, it will be ignored. Otherwise, the
        corresponding attribute will be updated. (Logging Level: INFO)
        """
        for key, value in kwargs.items():
            key = key.upper()
            if not hasattr(self, key):
                self.logger.info(f'Ignore unknown attribute "{key}"')
            else:
                setattr(self, key, value)
                self.logger.info(f'Attribute "{key}" has been updated to "{value}"')

        assert self.UI in self._SUPPORT_UI, "unsupported UI"
        assert self.MODE in self._SUPPORT_MODE, "unsupported MODE"
