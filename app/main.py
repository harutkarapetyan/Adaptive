from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
template = Jinja2Templates(directory="templates")

import base64

# Database and models
from database import engine, check_connection
from models.models import Base

# Define HTTPBasic security scheme
security = HTTPBasic()

# Routers
from api.auth.auth import auth_router
from api.endpoints.admin import admin_router
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
        if request.url.path in ["/docs", "/redoc", "/admin", "/openapi.json"]:
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

#CORS
app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],
     allow_methods=["*"],
     allow_headers=["*"],
     allow_credentials=True,
 )


app.add_middleware(
     DocsAuthMiddleware,
     auth_func=lambda credentials: get_current_user(credentials),
 )


@app.get("/")
def get_home_page(request: Request):
    return template.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return template.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("signup.html", {"request": request})

@app.get("/user-interface", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("user-interface.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("admin.html", {"request": request})

@app.get("/forgot", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("forgot.html", {"request": request})

@app.get("/admin-login", response_class=HTMLResponse)
def get_signup_page(request: Request):
    return template.TemplateResponse("admin-login.html", {"request": request})

# Protect the docs endpoints
@app.get("/docs")
async def get_docs():
     return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc")
async def get_redoc():
     return get_redoc_html(openapi_url="/openapi.json", title="redoc")



app.include_router(auth_router)
app.include_router(forgot_router)
app.include_router(admin_router)