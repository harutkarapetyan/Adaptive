from sqlalchemy import Column, Integer, String, ForeignKey, text, Boolean, DateTime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime, timedelta
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
    role = Column(String, nullable=True, default="user")  # New column for user role
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))


class ResetPassword(Base):
    __tablename__ = "password_reset"

    password_reset_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InvitationToken(Base):
    __tablename__ = "invitation_tokens"

    token = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))