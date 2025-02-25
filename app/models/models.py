from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, text, Boolean, Text, DateTime
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Boolean, nullable=True, server_default="False")
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))


class ResetPassword(Base):
    __tablename__ = "password_reset"

    password_reset_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    code = Column(Integer, nullable=False, unique=True)