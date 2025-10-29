from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.schemas import Token
from pydantic import BaseModel
from app.middleware.auth import create_access_token
from app.models import User
from app.config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_password_hash(password: str) -> str:
  return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def _ensure_default_admin(db: Session) -> None:
  admin = db.query(User).filter(User.username == settings.ADMIN_DEFAULT_USERNAME).first()
  if admin:
    return
  admin = User(
    username=settings.ADMIN_DEFAULT_USERNAME,
    email=settings.ADMIN_DEFAULT_EMAIL,
    hashed_password=_get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
    is_active=True,
    is_admin=True,
  )
  db.add(admin)
  db.commit()


class LoginRequest(BaseModel):
  username: str
  password: str


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
  """管理员登录，返回 JWT"""
  _ensure_default_admin(db)
  user = db.query(User).filter(User.username == payload.username).first()
  if not user or not _verify_password(payload.password, user.hashed_password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
  if not user.is_active:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
  access_token = create_access_token({"sub": user.username})
  return Token(access_token=access_token)


