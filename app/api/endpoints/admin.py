from fastapi import APIRouter,status, Depends, HTTPException
from services.service_email import send_email
from schemas.schemas import AdminLogin
from database import get_db
from core import  security
from models.models import User
from sqlalchemy.orm import  Session
from fastapi.responses import JSONResponse
import configparser


admin_router = APIRouter(tags=["admin"], prefix="/api/admin")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


config = configparser.ConfigParser()
config.read("./core/config.ini")

SERVER_ADDRESS = config["DEFAULT"]["SERVER_ADDRESS"]

def mail_invitation(name):

    URL = f"https://adaptive.ink/signup"

    return f"""
    Dear {name},
    We would like to invite you to join our private platform, Adaptive.
    To join, please use the following invitation link:  
    
    {URL}
    
    Please note that the link is valid for a limited time and can only be used once.
    Thank you.  
    We look forward to having you on board.

    Best regards,  
    The Adaptive Team
"""


subject = "Invitation to join Adaptive"
sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"

@admin_router.post("/mail_invitation_email")
def mail_invitation_email(email: str,name: str):
    send_email(subject, mail_invitation(name), sender, email, password)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message":"Message sent successfully."},
                        headers=headers)


@admin_router.post("/login_for_admin")
def login_for_admin(login_data: AdminLogin, db: Session = Depends(get_db)):
    user_email = login_data.email

    admin = db.query(User).filter(User.email == user_email, User.role == "admin").first()

    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email '{user_email}' was not found!")

    if not admin.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot log in because you have not completed authentication. Please check your email.")

    if not security.verify_password(login_data.password, admin.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Wrong password")

    access_token = security.create_access_token({"user_id": admin.user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Successfully logged in for admin!",
                            "access_token": access_token,
                            "id": admin.user_id
                        },
                        headers=headers)
