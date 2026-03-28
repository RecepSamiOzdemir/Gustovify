import secrets
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import config
import database
import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_refresh_token(user_id: int, db: Session) -> str:
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = models.RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at.date(),
        is_revoked=False
    )
    db.add(db_token)
    db.commit()
    return token


def verify_refresh_token(token: str, db: Session) -> models.User:
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token,
        models.RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Geçersiz refresh token")
    if db_token.expires_at < datetime.now(timezone.utc).date():
        db_token.is_revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token süresi dolmuş")
    return db.query(models.User).filter(models.User.id == db_token.user_id).first()


def revoke_refresh_token(token: str, db: Session):
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
