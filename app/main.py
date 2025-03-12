# FastAPI
from fastapi import FastAPI, status, Depends,HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

import base64

# Database and models
from database import engine, check_connection
from models.models import Base


# Define HTTPBasic security scheme
security = HTTPBasic()


# Routers
from api.auth.auth import auth_router
from api.auth.forgot_password import forgot_router


Base.metadata.create_all(bind=engine)
check_connection()

app = FastAPI(title="Adaptive Users")


# Simple user authentication for example purposes
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "Alfa2020"
    correct_password = "Beta2020"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Middleware to enforce authentication on docs and redoc
class DocsAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_func):
        super().__init__(app)
        self.auth_func = auth_func

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Basic "):
                return Response(content="Unauthorized",
                                status_code=HTTP_401_UNAUTHORIZED,
                                headers={"WWW-Authenticate": "Basic"})
            try:
                _, encoded = auth.split(' ')
                decoded = base64.b64decode(encoded).decode('utf-8')
                username, password = decoded.split(':')
                credentials = HTTPBasicCredentials(username=username, password=password)
                self.auth_func(credentials)
            except Exception:
                return Response(content="Unauthorized",
                                status_code=HTTP_401_UNAUTHORIZED,
                                headers={"WWW-Authenticate": "Basic"})
        response = await call_next(request)
        return response

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    DocsAuthMiddleware,
    auth_func=get_current_user,
)


@app.get("/")
def main():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "OK"})

# Protect the docs endpoints
@app.get("/docs", include_in_schema=False)
async def get_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    return app.openapi()


app.include_router(auth_router)
app.include_router(forgot_router)