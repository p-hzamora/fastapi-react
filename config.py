from __future__ import annotations
import logging
import os
from urllib.parse import urlparse

from backend.env import log, BACKEND_AUTH


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


DEFAULT_CONFIG = {
    "version": 0,
    "ui": {
        "default_locale": "",
    },
}


def get_config():
    return DEFAULT_CONFIG


CONFIG_DATA = get_config()


def get_config_value(config_path: str):
    path_parts = config_path.split(".")
    cur_config = CONFIG_DATA
    for key in path_parts:
        if key in cur_config:
            return cur_config[key]
    return None


PERSISTENT_CONFIG_REGISTRY: list[PersistentConfig] = []


class PersistentConfig[T]:
    def __init__(self, env_name: str, config_path: str, env_value: T):
        self._env_name = env_name
        self._config_path = config_path
        self._env_value = env_value

        self._config_value = get_config_value(config_path)
        if self._config_value is not None:
            log.info(f"'{env_name}' loaded from the latest database entry")
            self.value = self._config_value
        else:
            self.value = env_value

        PERSISTENT_CONFIG_REGISTRY.append(self)

    def __str__(self):
        return str(self.value)

    @property
    def __dict__(self):
        raise TypeError(
            "PersistentConfig object cannot be converted to dict, use config_get or .value instead."
        )

    def __getattribute__(self, item):
        if item == "__dict__":
            raise TypeError(
                "PersistentConfig object cannot be converted to dict, use config_get or .value instead."
            )
        return super().__getattribute__(item)

    # def update(self):
    #     new_value = get_config_value(self.config_path)
    #     if new_value is not None:
    #         self.value = new_value
    #         log.info(f"Updated {self.env_name} to new value {self.value}")

    # def save(self):
    #     log.info(f"Saving '{self.env_name}' to the database")
    #     path_parts = self.config_path.split(".")
    #     sub_config = CONFIG_DATA
    #     for key in path_parts[:-1]:
    #         if key not in sub_config:
    #             sub_config[key] = {}
    #         sub_config = sub_config[key]
    #     sub_config[path_parts[-1]] = self.value
    #     save_to_db(CONFIG_DATA)
    #     self.config_value = self.value


class AppConfig:
    _state: dict[str, PersistentConfig]

    def __init__(self):
        super().__setattr__("_state", {})

    def __setattr__(self, name, value):
        if isinstance(value, PersistentConfig):
            self._state[name] = value
        else:
            self._state[name].value = value
            # self._state[name].save()

    def __getattr__(self, key: str):
        return self._state[key].value


def validate_cors_origins(origins):
    for origin in origins:
        if origin != "*":
            validate_cors_origin(origin)


def validate_cors_origin(origin):
    parsed_url = urlparse(origin)

    # Check if the scheme is either http or https
    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError(
            f"Invalid scheme in CORS_ALLOW_ORIGIN: '{origin}'. Only 'http' and 'https' are allowed."
        )

    # Ensure that the netloc (domain + port) is present, indicating it's a valid URL
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL structure in CORS_ALLOW_ORIGIN: '{origin}'.")


CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*").split(";")

if "*" in CORS_ALLOW_ORIGIN:
    log.warning(
        "\n\nWARNING: CORS_ALLOW_ORIGIN IS SET TO '*' - NOT RECOMMENDED FOR PRODUCTION DEPLOYMENTS.\n"
    )

validate_cors_origins(CORS_ALLOW_ORIGIN)

SHOW_ADMIN_DETAILS = PersistentConfig(
    "SHOW_ADMIN_DETAILS",
    "auth.admin.show",
    os.environ.get("SHOW_ADMIN_DETAILS", "true").lower() == "true",
)

ADMIN_EMAIL = PersistentConfig(
    "ADMIN_EMAIL",
    "auth.admin.email",
    os.environ.get("ADMIN_EMAIL", None),
)


# class Config(Table):
#     __table_name__ = "config"

#     id: Column[int] = Column(int, primary_key=True)
#     data: Column[dict] = Column(json, nullable=False)
#     version: Column[int] = Column(Integer, nullable=False, default=0)
#     created_at: Column[datetime] = Column(DateTime, nullable=False, server_default=func.now())
#     updated_at: Column[datetime] = Column(DateTime, nullable=True, onupdate=func.now())


####################################
# BACKEND
####################################

BACKEND_URL = PersistentConfig(
    "BACKEND_URL", "backend.url", os.environ.get("BACKEND_URL", "http://localhost:3000")
)
ENABLE_SIGNUP = PersistentConfig(
    "ENABLE_SIGNUP",
    "ui.enable_signup",
    (
        False
        if not BACKEND_AUTH
        else os.environ.get("ENABLE_SIGNUP", "True").lower() == "true"
    ),
)

ENABLE_LOGIN_FORM = PersistentConfig(
    "ENABLE_LOGIN_FORM",
    "ui.ENABLE_LOGIN_FORM",
    os.environ.get("ENABLE_LOGIN_FORM", "True").lower() == "true",
)


####################################
# WEBUI_AUTH (Required for security)
####################################

ENABLE_API_KEY = PersistentConfig(
    "ENABLE_API_KEY",
    "auth.api_key.enable",
    os.environ.get("ENABLE_API_KEY", "True").lower() == "true",
)

ENABLE_API_KEY_ENDPOINT_RESTRICTIONS = PersistentConfig(
    "ENABLE_API_KEY_ENDPOINT_RESTRICTIONS",
    "auth.api_key.endpoint_restrictions",
    os.environ.get("ENABLE_API_KEY_ENDPOINT_RESTRICTIONS", "False").lower() == "true",
)

API_KEY_ALLOWED_ENDPOINTS = PersistentConfig(
    "API_KEY_ALLOWED_ENDPOINTS",
    "auth.api_key.allowed_endpoints",
    os.environ.get("API_KEY_ALLOWED_ENDPOINTS", ""),
)


JWT_EXPIRES_IN = PersistentConfig(
    "JWT_EXPIRES_IN", "auth.jwt_expiry", os.environ.get("JWT_EXPIRES_IN", "-1")
)


####################################
# OAuth config
####################################

ENABLE_OAUTH_SIGNUP = PersistentConfig(
    "ENABLE_OAUTH_SIGNUP",
    "oauth.enable_signup",
    os.environ.get("ENABLE_OAUTH_SIGNUP", "False").lower() == "true",
)

OAUTH_MERGE_ACCOUNTS_BY_EMAIL = PersistentConfig(
    "OAUTH_MERGE_ACCOUNTS_BY_EMAIL",
    "oauth.merge_accounts_by_email",
    os.environ.get("OAUTH_MERGE_ACCOUNTS_BY_EMAIL", "False").lower() == "true",
)
