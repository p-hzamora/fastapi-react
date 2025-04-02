import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import logging
import sys
from typing import Literal

from src.constants import ERROR_MESSAGES

SRC_DIR = Path(__file__).parent

BACKEND_DIR = SRC_DIR.parent
BASE_DIR = BACKEND_DIR.parent


try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(str(BASE_DIR / ".env")))

except ImportError:
    print("dotenv not installed, skipping...")


####################################
# LOGGING
####################################

type LogLevelType = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

log_levels: LogLevelType = [
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]
GLOBAL_LOG_LEVEL: LogLevelType = os.getenv("GLOBAL_LOG_LEVEL", "").upper()
if GLOBAL_LOG_LEVEL in log_levels:
    logging.basicConfig(
        stream=sys.stdout,
        level=GLOBAL_LOG_LEVEL,
        force=True,
        handlers=[logging.StreamHandler()],
    )
else:
    GLOBAL_LOG_LEVEL = "INFO"

log = logging.getLogger(__name__)
log.info(f"GLOBAL_LOG_LEVEL: {GLOBAL_LOG_LEVEL}")

type LogSourceType = Literal["CONFIG", "DB", "MAIN", "MODELS"]
log_sources = [
    "CONFIG",
    "DB",
    "MAIN",
    "MODELS",
]

SRC_LOG_LEVELS: dict[LogSourceType, LogLevelType] = {}

for source in log_sources:
    log_env_var = source + "_LOG_LEVEL"
    SRC_LOG_LEVELS[source] = os.getenv(log_env_var, "").upper()

    if SRC_LOG_LEVELS[source] not in log_levels:
        SRC_LOG_LEVELS[source] = GLOBAL_LOG_LEVEL

    log.info(f"{log_env_var}: {SRC_LOG_LEVELS[source]}")

log.setLevel(SRC_LOG_LEVELS["CONFIG"])


####################################
# Load DB variables
####################################

DB_USERNAME = os.getenv("DB_USERNAME", None)

DB_PASSWORD = os.getenv("DB_PASSWORD", None)

DB_DATABASE = os.getenv("DB_DATABASE", None)

DB_HOST = os.getenv("DB_HOST", "localhost")


if DB_USERNAME is None or DB_PASSWORD is None:
    raise ValueError(ERROR_MESSAGES.ENV_VAR_NOT_FOUND)


####################################
# ENV (dev, test, prod)
####################################

type PackageData = Literal["version"]
type EnvType = Literal["dev", "test", "prod"]

ENV: EnvType = os.getenv("ENV", "dev")
PACKAGE_DATA: dict[PackageData, str]

FROM_INIT_PY: bool = os.getenv("FROM_INIT_PY", "False").lower() == "true"
if FROM_INIT_PY:
    PACKAGE_DATA = {"version": importlib.metadata.version("fastapi-react")}
else:
    try:
        PACKAGE_DATA = json.loads((BASE_DIR / "package.json").read_text())
    except Exception:
        PACKAGE_DATA = {"version": "0.0.0"}

VERSION = PACKAGE_DATA["version"]


####################################
# BACKEND_AUTH (Required for security)
####################################


BACKEND_AUTH = os.getenv("BACKEND_AUTH", "True").lower() == "true"
BACKEND_AUTH_TRUSTED_EMAIL_HEADER = os.environ.get(
    "BACKEND_AUTH_TRUSTED_EMAIL_HEADER", None
)
BACKEND_AUTH_TRUSTED_NAME_HEADER = os.environ.get(
    "BACKEND_AUTH_TRUSTED_NAME_HEADER", None
)

BYPASS_MODEL_ACCESS_CONTROL = (
    os.environ.get("BYPASS_MODEL_ACCESS_CONTROL", "False").lower() == "true"
)


####################################
# BACKEND_SECRET_KEY
####################################

BACKEND_SECRET_KEY = os.environ.get(
    "BACKEND_SECRET_KEY",
    os.environ.get("BACKEND_JWT_SECRET_KEY", "t0p-s3cr3t"),  # DEPRECATED
)

BACKEND_SESSION_COOKIE_SAME_SITE = os.environ.get(
    "BACKEND_SESSION_COOKIE_SAME_SITE",
    os.environ.get("BACKEND_SESSION_COOKIE_SAME_SITE", "lax"),
)

BACKEND_SESSION_COOKIE_SECURE = os.environ.get(
    "BACKEND_SESSION_COOKIE_SECURE",
    os.environ.get("BACKEND_SESSION_COOKIE_SECURE", "false").lower() == "true",
)

if BACKEND_AUTH and BACKEND_SECRET_KEY == "":
    raise ValueError(ERROR_MESSAGES.ENV_VAR_NOT_FOUND)

ENABLE_WEBSOCKET_SUPPORT = (
    os.environ.get("ENABLE_WEBSOCKET_SUPPORT", "True").lower() == "true"
)

WEBSOCKET_MANAGER = os.environ.get("WEBSOCKET_MANAGER", "")

####################################
# BACKEND URI
####################################

API_VERSION = os.environ.get('API_VERSION', 'v1')

API_URI = f"/api/{API_VERSION}"
