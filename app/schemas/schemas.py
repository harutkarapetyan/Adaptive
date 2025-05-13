# For Data Validations
from pydantic import BaseModel, EmailStr

class  UserSignUp(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    phone_number: str
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    email: str
    code: int
    new_password: str
    confirm_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class InvitationRequest(BaseModel):
    email: str
    name: str


class ResetCodeRequest(BaseModel):
    email: str
    code: int