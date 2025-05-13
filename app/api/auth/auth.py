from fastapi import APIRouter, HTTPException, status, Depends, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.models import User, InvitationToken
from core import security
import re
from datetime import  datetime
from fastapi.responses import RedirectResponse
from core.confirm_registration import mail_verification_email
from schemas.schemas import UserLogin, UserSignUp
from database import get_db

auth_router = APIRouter(tags=["auth"], prefix="/api/auth")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}



def is_valid_password(password: str) -> bool:
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password) is not None


@auth_router.get("/mail_verification", name='mail_verification')
def verify_email(email: str = Query(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    user.status = True
    db.commit()
    db.refresh(user)
    return RedirectResponse(url="http://127.0.0.1:9100/login")


# @auth_router.post("/add-user")
# def add_user(user_signup_data: UserSignUp,
#              db: Session = Depends(get_db)):
#
#     if user_signup_data.password != user_signup_data.confirm_password:
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                             detail="Սխալ գաղտնաբառ")
#
#     # if not is_valid_password(user_signup_data.password):
#     #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#     #                     detail="Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character")
#
#     user_hashed_password = security.hash_password(user_signup_data.password)
#
#
#     if db.query(User).filter(User.email == user_signup_data.email).first():
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="Էլ․հասցեն արդեն առկա է")
#
#     # Insert user into database
#     new_user = User(
#         first_name=user_signup_data.first_name,
#         last_name =user_signup_data. last_name,
#         email=user_signup_data.email,
#         password=user_hashed_password,
#         phone_number=user_signup_data.phone_number,
#     )
#
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#
#     # Send verification email
#     mail_verification_email(user_signup_data.email)
#
#     return JSONResponse(status_code=status.HTTP_201_CREATED,
#                         content={"message": "Դուք հաջողությամբ գրանցվեցիք"})


@auth_router.post("/add-user")
def add_user(user_signup_data: UserSignUp,
             db: Session = Depends(get_db)):
    # 1. Սկզբում ստուգում ենք հրավերի token-ը
    invitation = db.query(InvitationToken).filter(InvitationToken.token == user_signup_data.token).first()

    if not invitation:
        raise HTTPException(status_code=400, detail="Հրավերը անվավեր է։")
    if invitation.is_used:
        raise HTTPException(status_code=400, detail="Հրավերը արդեն օգտագործվել է։")
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Հրավերի ժամկետը լրացել է։")

    # 2. Սովորական ստուգումներ
    if user_signup_data.password != user_signup_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Սխալ գաղտնաբառ")

    # if not is_valid_password(user_signup_data.password):
    #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #                         detail="Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character")

    user_hashed_password = security.hash_password(user_signup_data.password)

    if db.query(User).filter(User.email == user_signup_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Էլ․հասցեն արդեն առկա է")

    # 3. Ստեղծում ենք օգտատիրոջը
    new_user = User(
        first_name=user_signup_data.first_name,
        last_name=user_signup_data.last_name,
        email=user_signup_data.email,
        password=user_hashed_password,
        phone_number=user_signup_data.phone_number,
    )

    db.add(new_user)

    # 4. Հրավերի token-ը նշում ենք որպես օգտագործված
    invitation.is_used = True

    db.commit()
    db.refresh(new_user)

    # 5. Ուղարկում ենք հաստատման նամակ
    mail_verification_email(user_signup_data.email)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"message": "Դուք հաջողությամբ գրանցվեցիք"})


@auth_router.get("/get-one-user-by-id/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Error occurred while fetching user by id {user_id} ERROR: {error}')

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id {user_id} was not found!")

    # Return the user data as a JSON response
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"user_id": user.user_id, "first_name": user.first_name, "last_name": user.last_name,
                                 "email": user.email,"phone_number": user.phone_number,"status": user.status},
                        headers=headers)



@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.user_id == user_id).first()

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Օգտատեր չի հայտնաբերվել")

    try:
        db.delete(target_user)
        db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Հաջողությամբ ջնջվեց"}, headers=headers)


@auth_router.put("/update-user/{user_id}")
def update_user(user_id: int, first_name: str = Form(None), last_name: str = Form(None),
    email: str = Form(None), phone_number: str = Form(None), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" {user_id} id ունեցող օգտատեր չի հայտնաբերվել։",
        )

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:

        if db.query(User).filter(User.email == email, User.user_id != user_id).first():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="էլ․ հասցեն արդեն օգտագործված է",
            )
        user.email = email
    if phone_number:
        user.phone_number = phone_number

    try:
        db.commit()
        db.refresh(user)
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Օգտատիրոջ թարմացման խնդիր: {error}",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Օգտատիրոջ տվյալները հաջողությամբ թարմացվեցին",
            "user": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "status": user.status,
            },
        },
        headers=headers,
    )


@auth_router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user_email = login_data.email

    user = db.query(User).filter(User.email == user_email).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Այս էլ․ հասցեով օգտատեր '{user_email}' չի հայտնաբերվել!")

    if not user.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Դուք չեք կարող մուտք գործել, քանի որ չեք ավարտել նույնականացումը: Խնդրում ենք ստուգել ձեր էլ. հասցեն։")

    if not security.verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Սխալ գաղտնաբառ կամ օգտանուն")

    access_token = security.create_access_token({"user_id": user.user_id})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "Message": "Դուք հաջողությամբ մուտք գործեցիք!Ձեր թույլատվության թոքենն է՝",
                            "access_token": access_token,
                            "user_id": user.user_id,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "email": user.email,
                            "phone_number": user.phone_number,
                            "status": user.status
                        },
                        headers=headers)



@auth_router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()  # Get all users from the database
    return [{"user_id": user.user_id, "first_name": user.first_name, "last_name": user.last_name,
             "email": user.email, "phone_number": user.phone_number, "status": user.status} for user in users]
