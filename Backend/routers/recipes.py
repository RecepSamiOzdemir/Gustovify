from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import auth
import models
import schemas
import utils
import utils_scraper
from database import get_db
from dependencies import limiter
from helpers import get_or_create_master_ingredient, serialize_instructions

router = APIRouter(prefix="/recipes", tags=["Tarif İşlemleri"])


@router.post("/", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = models.Recipe(
        title=recipe.title,
        instructions=serialize_instructions(recipe.instructions),
        servings=recipe.servings,
        user_id=current_user.id
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for ing in recipe.ingredients:
        master_ing = get_or_create_master_ingredient(db, ing.name)
        normalized_unit = utils.normalize_unit(ing.unit)
        db_ingredient = models.RecipeIngredient(
            amount=ing.amount,
            unit=normalized_unit,
            is_special_unit=ing.is_special_unit,
            recipe_id=db_recipe.id,
            ingredient_id=master_ing.id
        )
        db.add(db_ingredient)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/")
def get_recipes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.Recipe).filter(models.Recipe.user_id == current_user.id)
    total = query.count()
    recipes = query.offset(skip).limit(limit).all()
    items = [schemas.Recipe.model_validate(r).model_dump() for r in recipes]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/suggest", tags=["Akıllı Analiz"])
def suggest_recipes(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipes = db.query(models.Recipe).filter(models.Recipe.user_id == current_user.id).all()
    inventory = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()

    suggestions = []
    for recipe in recipes:
        missing = utils.check_inventory_for_recipe(recipe.ingredients, inventory)
        suggestions.append({
            "recipe": recipe,
            "missing_count": len(missing),
            "missing_items": missing
        })

    suggestions.sort(key=lambda x: x["missing_count"])

    return [
        {
            **schemas.Recipe.model_validate(s["recipe"]).model_dump(),
            "missing_count": s["missing_count"]
        }
        for s in suggestions
    ]


@router.get("/{recipe_id}/scale/{target_servings}")
def get_scaled_recipe(recipe_id: int, target_servings: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")

    scaled_list = utils.scale_recipe(recipe.ingredients, recipe.servings, target_servings)
    return {
        "title": recipe.title,
        "original_servings": recipe.servings,
        "target_servings": target_servings,
        "scaled_ingredients": scaled_list
    }


@router.put("/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(recipe_id: int, recipe_update: schemas.RecipeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")

    if recipe_update.title:
        db_recipe.title = recipe_update.title
    if recipe_update.servings:
        db_recipe.servings = recipe_update.servings
    if recipe_update.instructions:
        db_recipe.instructions = serialize_instructions(recipe_update.instructions)

    if recipe_update.ingredients is not None:
        db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe_id).delete()
        for ing in recipe_update.ingredients:
            master_ing = get_or_create_master_ingredient(db, ing.name)
            normalized_unit = utils.normalize_unit(ing.unit)
            db_ingredient = models.RecipeIngredient(
                amount=ing.amount,
                unit=normalized_unit,
                is_special_unit=ing.is_special_unit,
                recipe_id=recipe_id,
                ingredient_id=master_ing.id
            )
            db.add(db_ingredient)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")

    db.delete(db_recipe)
    db.commit()
    return {"message": f"ID'si {recipe_id} olan tarif başarıyla silindi"}


@router.post("/scrape", response_model=schemas.ScrapeResponse, tags=["Scraper"])
@limiter.limit("10/minute")
def scrape_recipe(request: Request, scrape_req: schemas.ScrapeRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        data = utils_scraper.extract_recipe_from_url(scrape_req.url)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recipe_id}/check-stock", tags=["Akıllı Analiz"])
def check_recipe_stock(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")

    inventory = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()
    missing = utils.check_inventory_for_recipe(recipe.ingredients, inventory)
    return {
        "can_cook": len(missing) == 0,
        "missing_count": len(missing),
        "missing_items": missing
    }


@router.post("/{recipe_id}/cook", tags=["Akıllı Analiz"])
def cook_recipe(recipe_id: int, target_servings: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")

    inventory_items = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()
    servings_to_use = target_servings if target_servings and target_servings > 0 else recipe.servings
    scaled_ingredients = utils.scale_recipe(recipe.ingredients, recipe.servings, servings_to_use)

    inventory_dict = {item.name.lower(): item for item in inventory_items if item.name}
    deducted_items = []

    for scaled_ing in scaled_ingredients:
        name_lower = scaled_ing["name"].lower()
        if name_lower in inventory_dict:
            inv_item = inventory_dict[name_lower]
            new_amount = inv_item.amount - scaled_ing["scaled_amount"]
            if new_amount < 0:
                new_amount = 0
            inv_item.amount = round(new_amount * 100) / 100
            deducted_items.append({
                "name": inv_item.name,
                "deducted": scaled_ing["scaled_amount"],
                "remaining": inv_item.amount,
                "unit": inv_item.unit
            })

    db.commit()
    return {
        "message": "Pişirme işlemi tamamlandı, kiler güncellendi.",
        "deducted_items": deducted_items
    }
