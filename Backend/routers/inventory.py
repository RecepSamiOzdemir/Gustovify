from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import auth
import models
import schemas
import utils
from database import get_db
from helpers import get_or_create_master_ingredient

router = APIRouter(prefix="/inventory", tags=["Kiler İşlemleri"])


@router.post("/", response_model=schemas.Inventory)
def add_to_inventory(item: schemas.InventoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    master_ing = get_or_create_master_ingredient(db, item.name, item.category)

    db_item = db.query(models.Inventory).filter(
        models.Inventory.ingredient_id == master_ing.id,
        models.Inventory.user_id == current_user.id
    ).first()

    if db_item:
        db_item.amount += item.amount
        if item.category and not master_ing.category_id:
            get_or_create_master_ingredient(db, master_ing.name, item.category)
    else:
        item_data = item.dict(exclude={'name', 'category'})
        if 'unit' in item_data and item_data['unit']:
            item_data['unit'] = utils.normalize_unit(item_data['unit'])
        db_item = models.Inventory(**item_data, user_id=current_user.id, ingredient_id=master_ing.id)
        db.add(db_item)

    db.commit()
    db_item = db.query(models.Inventory).filter(models.Inventory.id == db_item.id).first()
    return db_item


@router.get("/")
def get_inventory(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.delete("/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id,
        models.Inventory.user_id == current_user.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    db.delete(db_item)
    db.commit()
    return {"message": "Ürün silindi"}


@router.put("/{item_id}", response_model=schemas.Inventory)
def update_inventory_item(item_id: int, item_update: schemas.InventoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id,
        models.Inventory.user_id == current_user.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    if item_update.amount is not None:
        db_item.amount = item_update.amount
    if item_update.unit is not None:
        db_item.unit = utils.normalize_unit(item_update.unit)
    if item_update.category is not None:
        get_or_create_master_ingredient(db, db_item.master_ingredient.name, item_update.category)
    if item_update.expiry_date is not None:
        db_item.expiry_date = item_update.expiry_date

    db.commit()
    db.refresh(db_item)
    return db_item
