from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import auth
import models
import schemas
import utils
from database import get_db
from helpers import get_or_create_master_ingredient

router = APIRouter(prefix="/shopping-list", tags=["Alışveriş Listesi"])


@router.post("/", response_model=schemas.ShoppingListItem)
def add_to_shopping_list(item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    master_ing = get_or_create_master_ingredient(db, item.name, item.category)

    db_item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.ingredient_id == master_ing.id,
        models.ShoppingListItem.user_id == current_user.id
    ).first()

    if db_item:
        db_item.amount += item.amount
        if item.category and not master_ing.category_id:
            get_or_create_master_ingredient(db, master_ing.name, item.category)
    else:
        item_data = item.dict(exclude={'name', 'category'})
        if 'unit' in item_data and item_data['unit']:
            item_data['unit'] = utils.normalize_unit(item_data['unit'])
        db_item = models.ShoppingListItem(**item_data, user_id=current_user.id, ingredient_id=master_ing.id)
        db.add(db_item)

    db.commit()
    db_item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == db_item.id).first()
    return db_item


@router.get("/")
def get_shopping_list(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.user_id == current_user.id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.put("/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(item_id: int, item_update: schemas.ShoppingListItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == item_id,
        models.ShoppingListItem.user_id == current_user.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    if item_update.amount is not None:
        db_item.amount = item_update.amount
    if item_update.unit is not None:
        db_item.unit = utils.normalize_unit(item_update.unit)
    if item_update.is_checked is not None:
        db_item.is_checked = item_update.is_checked
    if item_update.category is not None:
        get_or_create_master_ingredient(db, db_item.master_ingredient.name, item_update.category)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == item_id,
        models.ShoppingListItem.user_id == current_user.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    db.delete(db_item)
    db.commit()
    return {"message": "Ürün silindi"}


@router.post("/bulk-move")
def move_checked_items_to_inventory(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    checked_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == current_user.id,
        models.ShoppingListItem.is_checked == True
    ).all()

    moved_count = 0
    for s_item in checked_items:
        inv_item = db.query(models.Inventory).filter(
            models.Inventory.ingredient_id == s_item.ingredient_id,
            models.Inventory.user_id == current_user.id
        ).first()
        if inv_item:
            inv_item.amount += s_item.amount
        else:
            new_inv_item = models.Inventory(
                amount=s_item.amount,
                unit=s_item.unit,
                user_id=current_user.id,
                ingredient_id=s_item.ingredient_id
            )
            db.add(new_inv_item)
        db.delete(s_item)
        moved_count += 1

    db.commit()
    return {"message": f"{moved_count} ürün kilere taşındı."}
