from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/utils", tags=["Araçlar"])


@router.get("/allergens", response_model=List[schemas.Allergen])
def get_allergens(db: Session = Depends(get_db)):
    return db.query(models.Allergen).all()


@router.get("/preferences", response_model=List[schemas.DietaryPreference])
def get_preferences(db: Session = Depends(get_db)):
    return db.query(models.DietaryPreference).all()
