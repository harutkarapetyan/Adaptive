# from sqlalchemy.orm import Session
# from sqlalchemy import text, func
# from fastapi import APIRouter, HTTPException, status, Depends
# from fastapi.responses import JSONResponse
# import random
#
# from services.service_email import send_email
# from core import security
# from database import get_db
# from models.models import User, ResetPassword
# from services.db_service import get_row
# from schemas.schemas import ForgotPasswordRequest, ResetCodeRequest
#
# forgot_router = APIRouter(tags=["Forgot Password"], prefix="/api/password_reset")
#
# sender = "adaptiveproject2025@gmail.com"
# password = "whvu qagh hnug ukuz"
#
# @forgot_router.post("/request")
# def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     email = data.email
#
#     try:
#         target_user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=f"Server error: {error}")
#
#     if target_user is None:
#         raise HTTPException(status_code=404, detail="User with this email was not found.")
#
#     try:
#         code = random.randint(100000, 999999)
#
#         subject = "Գաղտնաբառի վերականգնման նամակ"
#         body = f"""Դուք ստացել եք այս նամակը, քանի որ խնդրել եք վերականգնել գաղտնաբառը։
#
#                     Կոդը՝ {code}
#
#                     Եթե դուք չեք խնդրել գաղտնաբառի փոփոխում, կարող եք անտեսել այս նամակը։"""
#
#         send_email(subject, body, sender, email, password)
#
#         reset_entry = ResetPassword(user_id=target_user.user_id, code=code)
#         db.add(reset_entry)
#         db.commit()
#         db.refresh(reset_entry)
#
#     except Exception as error:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to send reset email or save code: {error}")
#
#     return JSONResponse(status_code=200, content={"message": "Կոդը հաջողությամբ ուղարկվեց։"})
#
#
# @forgot_router.post('/verify-reset-code')
# def verify_reset_code(reset_request: ResetCodeRequest, db: Session = Depends(get_db)):
#     target_user = get_row(db, User, {"email": reset_request.email})
#     if not target_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found."
#         )
#
#     reset_record = get_row(db, ResetPassword, {"user_id": target_user.user_id})
#     if not reset_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Reset request not found."
#         )
#
#     if reset_record.code != reset_request.code:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired code."
#         )
#
#     return {"message": "Code verified successfully"}
#
#
#
#
#
# @forgot_router.post("/reset-password")
# def reset_password(data: dict, db: Session = Depends(get_db)):
#     email = data.get("email")
#     new_password = data.get("new_password")
#     confirm_password = data.get("confirm_password")
#
#     if not email or not new_password or not confirm_password:
#         raise HTTPException(status_code=400, detail="Missing fields.")
#
#     if new_password != confirm_password:
#         raise HTTPException(status_code=422, detail="Passwords do not match.")
#
#     try:
#         target_user = get_row(db, User, {"email": email})
#
#         if not target_user:
#             raise HTTPException(status_code=404, detail="User not found.")
#
#         hashed_password = security.hash_password(new_password)
#
#         db.execute(
#             text("UPDATE users SET password=:password WHERE email=:email"),
#             {"password": hashed_password, "email": email}
#         )
#
#         db.execute(
#             text("DELETE FROM password_reset WHERE user_id=:user_id"),
#             {"user_id": target_user.user_id}
#         )
#
#         db.commit()
#
#         return JSONResponse(status_code=200, content={"message": "Password reset successfully."})
#
#     except Exception as error:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Password reset error: {error}")
#







# from fastapi import APIRouter, Depends, HTTPException, status
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from database import get_db
# from models.models import User, ResetPassword
# from services.db_service import get_row
# from core.security import hash_password
# from fastapi.responses import JSONResponse
# from sqlalchemy import text
#
# forgot_router = APIRouter()
#
# # --- Pydantic Schemas ---
#
# class PasswordResetRequest(BaseModel):
#     email: str
#
# class ResetCodeVerify(BaseModel):
#     email: str
#     code: int
#
# class PasswordReset(BaseModel):
#     email: str
#     code: int
#     new_password: str
#     confirm_password: str
#
# # --- API Endpoints ---
#
# @forgot_router.post("/password_reset/request")
# def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
#     return {"message": "Reset code sent successfully"}
#
# @forgot_router.post("/password_reset/verify-reset-code")
# def verify_reset_code(reset_request: ResetCodeVerify, db: Session = Depends(get_db)):
#     target_user = get_row(db, User, {"email": reset_request.email})
#     if not target_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found."
#         )
#
#     reset_record = get_row(db, ResetPassword, {"user_id": target_user.user_id})
#     if not reset_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Reset request not found."
#         )
#
#     if reset_record.code != reset_request.code:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired code."
#         )
#
#     return {"message": "Code verified successfully"}
#
# @forgot_router.post("/forgot/reset")
# def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
#     if reset_data.new_password != reset_data.confirm_password:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="New password does not match"
#         )
#
#     target_user = get_row(db, User, {"email": reset_data.email})
#     if not target_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with email '{reset_data.email}' was not found"
#         )
#
#     reset = get_row(db, ResetPassword, {"user_id": target_user.user_id})
#     if not reset:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Reset request not found"
#         )
#
#     if reset_data.code != reset.code:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired reset code"
#         )
#
#     hashed_password = hash_password(reset_data.new_password)
#
#     try:
#         db.execute(
#             text("UPDATE users SET password=:password WHERE email=:email"),
#             {"password": hashed_password, "email": reset_data.email}
#         )
#
#         db.execute(
#             text("DELETE FROM password_reset WHERE user_id = :user_id AND code = :code"),
#             {"user_id": target_user.user_id, "code": reset_data.code}
#         )
#
#         db.commit()
#
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={"message": "Password changed successfully"}
#         )
#
#     except Exception as error:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail={"message": "Something went wrong", "detail": str(error)}
#         )











from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import random

from database import get_db
from models.models import User, ResetPassword
from services.service_email import send_email
from core import security
from services.db_service import get_row

forgot_router = APIRouter(tags=["Forgot Password"], prefix="/api/password_reset")

sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"

# ✅ 1. Կոդի ուղարկում
@forgot_router.post("/request")
def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Էլ. հասցեն պարտադիր է։")

    user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Օգտատերը չի գտնվել։")

    try:
        code = random.randint(100000, 999999)

        # Ջնջել նախորդ կոդերը
        db.query(ResetPassword).filter(ResetPassword.user_id == user.user_id).delete()

        # Ավելացնել նոր
        reset = ResetPassword(user_id=user.user_id, code=code)
        db.add(reset)
        db.commit()

        # Ուղարկել նամակ
        subject = "Գաղտնաբառի վերականգնման կոդ"
        body = f"Ձեր վերականգնման կոդն է՝ {code}"
        send_email(subject, body, sender, email, password)

        return JSONResponse(status_code=200, content={"message": "Կոդը հաջողությամբ ուղարկվեց։"})

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Սերվերի սխալ՝ {e}")


# ✅ 2. Կոդի ստուգում
@forgot_router.post("/verify-reset-code")
def verify_reset_code(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        raise HTTPException(status_code=400, detail="Տվյալները բացակայում են։")

    user = get_row(db, User, {"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Օգտատերը չի գտնվել։")

    reset = db.query(ResetPassword).filter(
        ResetPassword.user_id == user.user_id,
        ResetPassword.code == code
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Սխալ կամ ժամկետանց կոդ։")

    # Ստուգել ժամկետը
    if datetime.utcnow() - reset.created_at > timedelta(minutes=10):
        db.query(ResetPassword).filter(ResetPassword.user_id == user.user_id).delete()
        db.commit()
        raise HTTPException(status_code=400, detail="Կոդի ժամկետն ավարտվել է։")

    return JSONResponse(status_code=200, content={"message": "Կոդը հաստատվել է։"})




# ✅ 3. Գաղտնաբառի վերականգնում
@forgot_router.post("/reset-password")
def reset_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all([email, code, new_password, confirm_password]):
        raise HTTPException(status_code=400, detail="Բոլոր դաշտերը պարտադիր են։")

    if new_password != confirm_password:
        raise HTTPException(status_code=422, detail="Գաղտնաբառերը չեն համընկնում։")

    user = get_row(db, User, {"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Օգտատերը չի գտնվել։")

    reset = db.query(ResetPassword).filter(
        ResetPassword.user_id == user.user_id,
        ResetPassword.code == code
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Սխալ կամ ժամկետանց կոդ։")

    if datetime.utcnow() - reset.created_at > timedelta(minutes=10):
        db.query(ResetPassword).filter(ResetPassword.user_id == user.user_id).delete()
        db.commit()
        raise HTTPException(status_code=400, detail="Կոդի ժամկետն ավարտվել է։")

    try:
        hashed = security.hash_password(new_password)
        db.execute(text("UPDATE users SET password=:password WHERE email=:email"),
                   {"password": hashed, "email": email})
        db.query(ResetPassword).filter(ResetPassword.user_id == user.user_id).delete()
        db.commit()

        return JSONResponse(status_code=200, content={"message": "Գաղտնաբառը հաջողությամբ վերականգնվել է։"})

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Սխալ՝ {e}")
