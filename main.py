from pathlib import Path
import time
from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware
import sys

sys.path.append(str(Path(__file__).parent.parent))

from backend.env import (
    ENV,
    BACKEND_AUTH_TRUSTED_EMAIL_HEADER,
    BACKEND_AUTH_TRUSTED_NAME_HEADER,
)
from backend.config import (
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
from backend.domain.auth.routers import auth
from backend.domain.user.routers import user


# Dummy user data
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

app = FastAPI(
    docs_url="/docs" if ENV == "dev" else None,
    openapi_url="/openapi.json" if ENV == "dev" else None,
    redoc_url=None,
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
async def check_url(request: Request, call_next):
    start_time = int(time.time())
    request.state.enable_api_key = app.state.config.ENABLE_API_KEY
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


BACKEND_API_BASE_URL = "api/v1"
app.include_router(auth.router, prefix=f"/{BACKEND_API_BASE_URL}/auth", tags=["auths"])
app.include_router(user.router, prefix=f"/{BACKEND_API_BASE_URL}/user", tags=["user"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0",port=8000)
