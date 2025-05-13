from fastapi import APIRouter,status, Depends, HTTPException
from services.service_email import send_email
from schemas.schemas import AdminLogin, InvitationRequest
from database import get_db
from core import  security
from models.models import User, InvitationToken
from sqlalchemy.orm import  Session
from fastapi.responses import JSONResponse
import configparser
from datetime import datetime, timedelta
import uuid
from core.urls import INVITATION_BASE_URL


admin_router = APIRouter(tags=["admin"], prefix="/api/admin")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}



def mail_invitation(name, invitation_url):
    return f"""
    Հարգելի {name},
    Մենք կցանկանայինք հրավիրել ձեզ միանալ մեր մասնավոր հարթակին՝ Adaptive-ին։

    Միանալու համար, խնդրում ենք օգտագործել հետևյալ հրավերի հղումը՝  

    <a href="{invitation_url}">{invitation_url}</a>


    Խնդրում ենք նկատի ունենալ, որ հղումը վավեր է 24 ժամ և կարող է օգտագործվել միայն մեկ անգամ։
    Շնորհակալություն։
    Մենք անհամբեր սպասում ենք ձեզ տեսնել մեր թիմում։

    Հարգանքներով՝
    Adaptive թիմ
    """



subject = "Հրավեր՝ միանալու Adaptive-ին"
sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"



# @admin_router.post("/mail_invitation_email")
# def mail_invitation_email(data: InvitationRequest, db: Session = Depends(get_db)):
#     # Սկզբում ստուգում ենք գոյություն ունեցող հրավերը
#     existing_invitation = db.query(InvitationToken).filter(InvitationToken.email == data.email).first()
#
#     if existing_invitation:
#         # Եթե հրավերը ակտիվ է (չի օգտագործվել և ժամկետը չի լրացել), ապա արգելում ենք
#         if not existing_invitation.is_used and existing_invitation.expires_at > datetime.utcnow():
#             raise HTTPException(status_code=400, detail="Այս էլ․ հասցեի համար արդեն ուղարկվել է հրավերի հղում։")
#         else:
#             # Եթե հրավերը օգտագործված է կամ ժամկետը լրացել է, ջնջում ենք հին հրավերը
#             db.delete(existing_invitation)
#             db.commit()
#
#     # Ստեղծում ենք նոր հրավեր
#     new_token = InvitationToken(
#         token=str(uuid.uuid4()),
#         email=data.email,
#         expires_at=datetime.utcnow() + timedelta(hours=24)
#     )
#     db.add(new_token)
#     db.commit()
#     db.refresh(new_token)
#
#     # Ուղարկում ենք նամակ
#     invitation_url = f"http://127.0.0.1:9000/signup?token={new_token.token}"
#     send_email(subject, mail_invitation(data.name, invitation_url), sender, data.email, password)
#
#     return JSONResponse(status_code=status.HTTP_200_OK,
#                         content={"message": "Message sent successfully."},
#                         headers=headers)

@admin_router.post("/mail_invitation_email")
def mail_invitation_email(data: InvitationRequest, db: Session = Depends(get_db)):
    existing_invitation = db.query(InvitationToken).filter(InvitationToken.email == data.email).first()

    if existing_invitation:
        if not existing_invitation.is_used and existing_invitation.expires_at > datetime.utcnow():
            raise HTTPException(status_code=400, detail="Այս էլ․ հասցեի համար արդեն ուղարկվել է հրավերի հղում։")
        else:
            db.delete(existing_invitation)
            db.commit()

    new_token = InvitationToken(
        token=str(uuid.uuid4()),
        email=data.email,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    invitation_url = f"{INVITATION_BASE_URL}?token={new_token.token}"
    send_email(subject, mail_invitation(data.name, invitation_url), sender, data.email, password)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Message sent successfully."},
                        headers=headers)


@admin_router.post("/login_for_admin")
def login_for_admin(login_data: AdminLogin, db: Session = Depends(get_db)):
    user_email = login_data.email

    admin = db.query(User).filter(User.email == user_email, User.role == "admin").first()

    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"'{user_email}' էլ․ հասցեով ադմին գոյություն չունի")

    if not admin.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Դուք չեք կարող մուտք գործել, քանի որ չեք ավարտել նույնականացումը: Խնդրում ենք ստուգել ձեր էլ. հասցեն։")

    if not security.verify_password(login_data.password, admin.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Սխալ գաղտնաբառ")

    access_token = security.create_access_token({"user_id": admin.user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Հաջողությամբ մուտք գործեցիք որպես ադմին!",
                            "access_token": access_token,
                            "id": admin.user_id
                        },
                        headers=headers)

@admin_router.get("/validate-invite")
def validate_invite(token: str, db: Session = Depends(get_db)):
    invitation = db.query(InvitationToken).filter(InvitationToken.token == token).first()

    if not invitation:
        raise HTTPException(status_code=400, detail="Հրավերը անվավեր է։")

    if invitation.is_used:
        raise HTTPException(status_code=400, detail="Հրավերը արդեն օգտագործվել է։")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Հրավերի ժամկետը լրացել է։")

    return {"message": "Հրավերը վավեր է։"}