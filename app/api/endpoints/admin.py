from fastapi import APIRouter, HTTPException, status, Depends, Form
from services.service_email import send_email
import re
import configparser


admin_router = APIRouter(tags=["admin"], prefix="/api/admin")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}


config = configparser.ConfigParser()
config.read("./core/config.ini")

SERVER_ADDRESS = config["DEFAULT"]["SERVER_ADDRESS"]


def mail_invitation(email):

    URL = f"{SERVER_ADDRESS}/api/auth/add-user"

    return f"""Dear user,
               Thank you for creating your account.
               Please confirm your email address. The confirmation code is:
            \n
            {URL}/{email}
            \n
              If you have not requested a verification code, you can safely ignore this email․
    """


subject = "Invitation to join Adaptive"
sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"


def mail_invitation_email(email):
    send_email(subject, mail_invitation(email), sender, email, password)
