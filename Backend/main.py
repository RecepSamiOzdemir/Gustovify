import json
from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import models, database, schemas, utils, auth, utils_scraper, config
from database import get_db

# Veritabanı tablolarını otomatik oluştur
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gustovify API", version="1.4")

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — config'ten okunan origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Gustovify Veritabanı Bağlantısı Aktif"}


# --- YARDIMCI FONKSİYONLAR ---

def get_or_create_master_ingredient(db: Session, name: str, category_name: str = None) -> models.MasterIngredient:
    if not name:
        return None
    name_clean = name.strip().title()
    master = db.query(models.MasterIngredient).filter(models.MasterIngredient.name == name_clean).first()

    category_obj = None
    if category_name:
        category_clean = category_name.strip().title()
        category_obj = db.query(models.Category).filter(models.Category.name == category_clean).first()
        if not category_obj:
            category_obj = models.Category(name=category_clean)
            db.add(category_obj)
            db.commit()
            db.refresh(category_obj)

    if not master:
        master = models.MasterIngredient(
            name=name_clean,
            category_id=category_obj.id if category_obj else None
        )
        db.add(master)
        db.commit()
        db.refresh(master)
    elif not master.category_id and category_obj:
        master.category_id = category_obj.id
        db.commit()
        db.refresh(master)

    return master


def parse_instructions(instructions_str: str) -> list:
    """DB'den gelen instructions string'ini listeye çevirir."""
    if not instructions_str:
        return []
    # Önce JSON olarak parse etmeyi dene (yeni format)
    try:
        parsed = json.loads(instructions_str)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    # Eski pipe-delimited format için fallback
    return [s.strip() for s in instructions_str.split("|") if s.strip()]


def serialize_instructions(instructions: list) -> str:
    """Instructions listesini JSON string'e çevirir."""
    return json.dumps(instructions, ensure_ascii=False)


# --- TARİF ENDPOINTLERİ (Auth korumalı) ---

@app.post("/recipes/", response_model=schemas.Recipe, tags=["Tarif İşlemleri"])
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
    db_recipe.instructions = parse_instructions(db_recipe.instructions)
    return db_recipe


@app.get("/recipes/", response_model=List[schemas.Recipe], tags=["Tarif İşlemleri"])
def get_recipes(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipes = db.query(models.Recipe).filter(models.Recipe.user_id == current_user.id).all()
    for r in recipes:
        r.instructions = parse_instructions(r.instructions)
    return recipes


@app.get("/recipes/{recipe_id}/scale/{target_servings}", tags=["Tarif İşlemleri"])
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


@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe, tags=["Tarif İşlemleri"])
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
    db_recipe.instructions = parse_instructions(db_recipe.instructions)
    return db_recipe


@app.delete("/recipes/{recipe_id}", tags=["Tarif İşlemleri"])
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


@app.post("/recipes/scrape", response_model=schemas.ScrapeResponse, tags=["Scraper"])
@limiter.limit("10/minute")
def scrape_recipe(request: Request, scrape_req: schemas.ScrapeRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        data = utils_scraper.extract_recipe_from_url(scrape_req.url)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/recipes/{recipe_id}/check-stock", tags=["Akıllı Analiz"])
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


@app.get("/recipes/suggest", tags=["Akıllı Analiz"])
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
            "id": s["recipe"].id,
            "title": s["recipe"].title,
            "instructions": parse_instructions(s["recipe"].instructions),
            "servings": s["recipe"].servings,
            "ingredients": s["recipe"].ingredients,
            "missing_count": s["missing_count"]
        }
        for s in suggestions
    ]


@app.post("/recipes/{recipe_id}/cook", tags=["Akıllı Analiz"])
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


# --- KİLER ENDPOINTLERİ ---

@app.post("/inventory/", response_model=schemas.Inventory, tags=["Kiler İşlemleri"])
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


@app.get("/inventory/", response_model=List[schemas.Inventory], tags=["Kiler İşlemleri"])
def get_inventory(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()


@app.delete("/inventory/{item_id}", tags=["Kiler İşlemleri"])
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


@app.put("/inventory/{item_id}", response_model=schemas.Inventory, tags=["Kiler İşlemleri"])
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


# --- ALIŞVERİŞ LİSTESİ ENDPOINTLERİ ---

@app.post("/shopping-list/", response_model=schemas.ShoppingListItem, tags=["Alışveriş Listesi"])
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


@app.get("/shopping-list/", response_model=List[schemas.ShoppingListItem], tags=["Alışveriş Listesi"])
def get_shopping_list(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.user_id == current_user.id).all()


@app.put("/shopping-list/{item_id}", response_model=schemas.ShoppingListItem, tags=["Alışveriş Listesi"])
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


@app.delete("/shopping-list/{item_id}", tags=["Alışveriş Listesi"])
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


@app.post("/shopping-list/bulk-move", tags=["Alışveriş Listesi"])
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


# --- AUTH ENDPOINTLERİ ---

@app.post("/auth/register", response_model=schemas.User, tags=["Kimlik Doğrulama"])
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


@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Kimlik Doğrulama"])
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


@app.post("/auth/refresh", response_model=schemas.TokenResponse, tags=["Kimlik Doğrulama"])
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


@app.post("/auth/logout", tags=["Kimlik Doğrulama"])
def logout(body: schemas.RefreshRequest, db: Session = Depends(get_db)):
    auth.revoke_refresh_token(body.refresh_token, db)
    return {"message": "Çıkış yapıldı"}


# --- KULLANICI ENDPOINTLERİ ---

@app.get("/users/me", response_model=schemas.User, tags=["Kullanıcı"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.put("/users/me", response_model=schemas.User, tags=["Kullanıcı"])
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


# --- ARAÇ ENDPOINTLERİ ---

@app.get("/utils/allergens", response_model=List[schemas.Allergen], tags=["Araçlar"])
def get_allergens(db: Session = Depends(get_db)):
    return db.query(models.Allergen).all()


@app.get("/utils/preferences", response_model=List[schemas.DietaryPreference], tags=["Araçlar"])
def get_preferences(db: Session = Depends(get_db)):
    return db.query(models.DietaryPreference).all()
