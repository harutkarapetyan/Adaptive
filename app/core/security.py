import datetime

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer

from models.models import User
from database import get_db
from sqlalchemy.orm import Session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUETS = 43200
ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_SECRET = "SECRET"

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    try:
        payload = data.copy()
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUETS)
        payload.update({"exp": expire_time})

        access_token = jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm=ACCESS_TOKEN_ALGORITHM)

        return access_token
    except Exception as err:
        return err


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[ACCESS_TOKEN_ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception



def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = verify_token(token, credentials_exception)

        user_id = payload.get("user_id")

        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise credentials_exception

        return user
    except Exception as error:
        raise error

