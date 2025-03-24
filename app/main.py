# FastAPI
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Database and models
from database import engine, check_connection
from models.models import Base


# Routers
from api.auth.auth import auth_router
from api.auth.forgot_password import forgot_router


Base.metadata.create_all(bind=engine)
check_connection()

app = FastAPI()

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def main():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "OK"})



app.include_router(auth_router)
app.include_router(forgot_router)