# For Data Validations
from pydantic import BaseModel, EmailStr

class  UserSignUp(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    phone_number: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    email: str
    code: int
    new_password: str
    confirm_password: str
