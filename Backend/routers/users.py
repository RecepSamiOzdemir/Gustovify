from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import get_db

router = APIRouter(prefix="/users", tags=["Kullanıcı"])


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if user_update.password:
        user.hashed_password = auth.get_password_hash(user_update.password)
    if user_update.allergen_ids is not None:
        user.related_allergens = db.query(models.Allergen).filter(models.Allergen.id.in_(user_update.allergen_ids)).all()
    if user_update.preference_ids is not None:
        user.related_preferences = db.query(models.DietaryPreference).filter(models.DietaryPreference.id.in_(user_update.preference_ids)).all()
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.city is not None:
        user.city = user_update.city
    if user_update.age is not None:
        user.age = user_update.age
    if user_update.gender is not None:
        user.gender = user_update.gender
    if user_update.cooking_level is not None:
        user.cooking_level = user_update.cooking_level

    db.commit()
    db.refresh(user)
    return user
