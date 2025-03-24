from fastapi import APIRouter, HTTPException, status, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.models import User
from core import security
import re
from core.confirm_registration import mail_verification_email
from schemas.schemas import UserLogin, UserSignUp
from database import get_db

admin_router = APIRouter(tags=["admin"], prefix="/api/admin")

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type, Authorization",
           "Access-Control-Allow-Credentials": "true"}

