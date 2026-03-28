from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth
import config
import models
import schemas
from database import get_db
from dependencies import limiter

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=schemas.User)
@limiter.limit("5/minute")
def register_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı")

    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)

    if user.allergen_ids:
        db_user.related_allergens = db.query(models.Allergen).filter(models.Allergen.id.in_(user.allergen_ids)).all()
    if user.preference_ids:
        db_user.related_preferences = db.query(models.DietaryPreference).filter(models.DietaryPreference.id.in_(user.preference_ids)).all()

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
def refresh_access_token(request: Request, body: schemas.RefreshRequest, db: Session = Depends(get_db)):
    user = auth.verify_refresh_token(body.refresh_token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz refresh token")

    auth.revoke_refresh_token(body.refresh_token, db)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = auth.create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(body: schemas.RefreshRequest, db: Session = Depends(get_db)):
    auth.revoke_refresh_token(body.refresh_token, db)
    return {"message": "Çıkış yapıldı"}
