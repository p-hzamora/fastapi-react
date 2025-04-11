from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware
import sys

from starlette.middleware.base import RequestResponseEndpoint
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.env import (
    ENV,
    BACKEND_AUTH_TRUSTED_EMAIL_HEADER,
    BACKEND_AUTH_TRUSTED_NAME_HEADER,
    SRC_LOG_LEVELS,
    API_URI,
    DB_DATABASE,
)
from src.core.config import (
    CORS_ALLOW_ORIGIN,
    # Task
    BACKEND_URL,
    ENABLE_SIGNUP,
    ENABLE_LOGIN_FORM,
    ENABLE_API_KEY,
    ENABLE_API_KEY_ENDPOINT_RESTRICTIONS,
    API_KEY_ALLOWED_ENDPOINTS,
    JWT_EXPIRES_IN,
    SHOW_ADMIN_DETAILS,
    ADMIN_EMAIL,
    AppConfig,
)
from src.domain.auth.routers import auth
from src.domain.user.routers import user
from src.domain.todos.routers import todos

from src.core import db
from src.domain.auth.models import Auth
from src.domain.user.models import User
from src.domain.todos.models import Todo

from ormlambda import ORM

if not db.database_exists(DB_DATABASE):
    db.create_database(DB_DATABASE, "fail")
    db.database = DB_DATABASE
    ORM(Auth, db).create_table()
    ORM(User, db).create_table()
    ORM(Todo, db).create_table()


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starts API REST")
    yield
    log.info("Ends API REST")


app = FastAPI(
    swagger_ui_parameters={
        "syntaxHighlight.theme": "obsidian",
    },
    docs_url="/docs" if ENV == "dev" else None,
    openapi_url="/openapi.json" if ENV == "dev" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.config = AppConfig()

########################################
#
# BACKEND
#
########################################

app.state.config.BACKEND_URL = BACKEND_URL
app.state.config.ENABLE_SIGNUP = ENABLE_SIGNUP
app.state.config.ENABLE_LOGIN_FORM = ENABLE_LOGIN_FORM

app.state.config.ENABLE_API_KEY = ENABLE_API_KEY
app.state.config.ENABLE_API_KEY_ENDPOINT_RESTRICTIONS = (
    ENABLE_API_KEY_ENDPOINT_RESTRICTIONS
)
app.state.config.API_KEY_ALLOWED_ENDPOINTS = API_KEY_ALLOWED_ENDPOINTS

app.state.config.JWT_EXPIRES_IN = JWT_EXPIRES_IN

app.state.config.SHOW_ADMIN_DETAILS = SHOW_ADMIN_DETAILS
app.state.config.ADMIN_EMAIL = ADMIN_EMAIL


app.state.AUTH_TRUSTED_EMAIL_HEADER = BACKEND_AUTH_TRUSTED_EMAIL_HEADER
app.state.AUTH_TRUSTED_NAME_HEADER = BACKEND_AUTH_TRUSTED_NAME_HEADER

app.state.TOOLS = {}
app.state.FUNCTIONS = {}


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_url(request: Request, call_next: RequestResponseEndpoint):
    start_time = int(time.time())
    request.state.enable_api_key = app.state.config.ENABLE_API_KEY
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(todos.router, prefix=f"{API_URI}/todo", tags=["todos"])
app.include_router(auth.router, prefix=f"{API_URI}/auth", tags=["auths"])
app.include_router(user.router, prefix=f"{API_URI}/user", tags=["user"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
