from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from utils import scale_recipe
from fastapi.middleware.cors import CORSMiddleware

import models, database, schemas, utils, auth, utils_scraper # Hazırladığın dosyaları içe aktarıyoruz
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# TDD 4.1: Veritabanı tablolarını otomatik oluştur (gustovify.db dosyası oluşur)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gustovify API", version="1.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında her yerden erişime izin verir
    allow_methods=["*"],
    allow_headers=["*"],
)
# Veritabanı bağlantısı için yardımcı fonksiyon (Dependency)
from database import get_db

@app.get("/")
def read_root():
    return {"status": "online", "message": "Gustovify Veritabanı Bağlantısı Aktif"}


# Yardımcı Fonksiyon: MasterIngredient Bul veya Oluştur
def get_or_create_master_ingredient(db: Session, name: str, category_name: str = None) -> models.MasterIngredient:
    if not name:
        return None
    name_clean = name.strip().title()
    master = db.query(models.MasterIngredient).filter(models.MasterIngredient.name == name_clean).first()
    
    # Kategori Bul veya Oluştur (Eğer gönderildiyse)
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
    # Eğer master zaten varsa ama kategorisi yoksa ve yeni kategori geldiyse güncelle
    elif not master.category_id and category_obj:
        master.category_id = category_obj.id
        db.commit()
        db.refresh(master)
        
    return master

# TDD 3.1 & 3.2: Yeni tarif kaydetme ve kilerle ilişkilendirme temeli
@app.post("/recipes/", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    # 1. Önce ana tarif kaydını oluştur
    db_recipe = models.Recipe(
        title=recipe.title,
        instructions="|".join(recipe.instructions), # Listeyi string olarak birleştiriyoruz
        servings=recipe.servings
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    # 2. Malzemeleri semantik olarak tarifle ilişkilendirerek kaydet
    for ing in recipe.ingredients:
        # Master Ingredient kontrolü
        master_ing = get_or_create_master_ingredient(db, ing.name)
        
        # Birim normalizasyonu
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

    db_recipe.instructions = db_recipe.instructions.split("|")
    return db_recipe

# Kayıtlı tüm tarifleri getirme
@app.get("/recipes/", response_model=List[schemas.Recipe])
def get_recipes(db: Session = Depends(get_db)):
    recipies = db.query(models.Recipe).all()
    for r in recipies:
        r.instructions = r.instructions.split("|")
    return recipies

@app.get("/recipes/{recipe_id}/scale/{target_servings}")
def get_scaled_recipe(recipe_id: int, target_servings: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
    
    scaled_list = utils.scale_recipe(recipe.ingredients, recipe.servings, target_servings)
    
    return {
        "title": recipe.title,
        "original_servings": recipe.servings,
        "target_servings": target_servings,
        "scaled_ingredients": scaled_list
    }

@app.post("/inventory/", response_model=schemas.Inventory, tags=["Kiler İşlemleri"])
def add_to_inventory(item: schemas.InventoryCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Kullanıcıya özel ürün kontrolü
    # Önce Master Ingredient'i bul/oluştur
    master_ing = get_or_create_master_ingredient(db, item.name, item.category)
    
    db_item = db.query(models.Inventory).filter(
        models.Inventory.ingredient_id == master_ing.id,
        models.Inventory.user_id == current_user.id
    ).first()
    
    if db_item:
        db_item.amount += item.amount # Varsa üzerine ekle
        # Birimi güncelleme mantığı (İsteğe bağlı, yeni gelen daha standart olabilir)
        # db_item.unit = utils.normalize_unit(item.unit)
        
        # Eğer yeni kategori bilgisi geldiyse ve master'ın kategorisi yoksa güncelle
        if item.category and not master_ing.category_id:
             get_or_create_master_ingredient(db, master_ing.name, item.category) # Master'ı günceller
             
    else:
        # User ID ile yeni kayıt
        # item.dict() içindeki 'name' ve 'category' alanını çıkarıyoruz çünkü modelde yok
        item_data = item.dict(exclude={'name', 'category'})
        # Birim normalizasyonu
        if 'unit' in item_data and item_data['unit']:
             item_data['unit'] = utils.normalize_unit(item_data['unit'])
             
        db_item = models.Inventory(**item_data, user_id=current_user.id, ingredient_id=master_ing.id)
        db.add(db_item)
    db.commit()
    db_item = db.query(models.Inventory).filter(models.Inventory.id == db_item.id).first() # Refresh with relations
    return db_item

@app.get("/inventory/", response_model=List[schemas.Inventory], tags=["Kiler İşlemleri"])
def get_inventory(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Sadece giriş yapan kullanıcının malzemelerini getir
    return db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()

@app.delete("/recipes/{recipe_id}", tags=["Tarif İşlemleri"])
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
    
    # TDD 4.1: İlişkili malzemelerle birlikte siler
    db.delete(db_recipe)
    db.commit()
    return {"message": f"ID'si {recipe_id} olan tarif başarıyla silindi"}

@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe, tags=["Tarif İşlemleri"])
def update_recipe(recipe_id: int, recipe_update: schemas.RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
    
    # Temel bilgileri güncelle
    if recipe_update.title:
        db_recipe.title = recipe_update.title
    if recipe_update.servings:
        db_recipe.servings = recipe_update.servings
    if recipe_update.instructions:
        db_recipe.instructions = "|".join(recipe_update.instructions)
        
    # Malzemeleri güncelle (Bu kısım biraz kompleks: sil-ekle veya güncelle mantığı)
    # Basit yaklaşım: Mevcut malzemeleri sil, yenilerini ekle (MVP için yeterli)
    if recipe_update.ingredients is not None:
        # Önce eskileri sil (RecipeIngredient)
        db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe_id).delete()
        
        # Yenileri ekle
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
    db_recipe.instructions = db_recipe.instructions.split("|")
    return db_recipe

@app.delete("/inventory/{item_id}", tags=["Kiler İşlemleri"])
def delete_inventory_item(item_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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
def update_inventory_item(item_id: int, item_update: schemas.InventoryUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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
        # Kategoriyi inventory item üzerinden değil, master ingredient üzerinden güncellemeliyiz
        # Bu işlem tüm kullanıcıları etkiler mi? Evet, MasterIngredient küreseldir.
        # Ancak şimdilik basitlik adına: Eğer Master'ın kategorisi yoksa veya değiştirilmek isteniyorsa güncelle.
        # NOT: Gerçek hayatta bu işlem için ayrı bir ADMIN endpoint'i daha doğru olur.
        # MVP Çözüm: Master Ingredient fonksiyonunu çağırıp güncelleme yaptıralım.
        get_or_create_master_ingredient(db, db_item.master_ingredient.name, item_update.category)
        
    if item_update.expiry_date is not None:
        db_item.expiry_date = item_update.expiry_date
        
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/shopping-list/", response_model=schemas.ShoppingListItem, tags=["Alışveriş Listesi"])
def add_to_shopping_list(item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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
def get_shopping_list(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.user_id == current_user.id).all()

@app.put("/shopping-list/{item_id}", response_model=schemas.ShoppingListItem, tags=["Alışveriş Listesi"])
def update_shopping_list_item(item_id: int, item_update: schemas.ShoppingListItemUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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
def delete_shopping_list_item(item_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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
def move_checked_items_to_inventory(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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

@app.get("/recipes/{recipe_id}/check-stock", tags=["Akıllı Analiz"])
def check_recipe_stock(recipe_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    # Kullanıcının kilerini getir
    inventory = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
        
    missing = utils.check_inventory_for_recipe(recipe.ingredients, inventory)
    
    return {
        "can_cook": len(missing) == 0,
        "missing_count": len(missing),
        "missing_items": missing
    }

@app.get("/recipes/suggest", tags=["Akıllı Analiz"])
def suggest_recipes(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    recipes = db.query(models.Recipe).all()
    # Sadece kullanıcının kilerine göre öneri yap
    inventory = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()
    
    suggestions = []
    
    for recipe in recipes:
        missing = utils.check_inventory_for_recipe(recipe.ingredients, inventory)
        suggestions.append({
            "recipe": recipe,
            "missing_count": len(missing),
            "missing_items": missing
        })
    
    # Eksik malzeme sayısına göre sırala (en az eksik olan en üstte)
    suggestions.sort(key=lambda x: x["missing_count"])
    
    # Response model uyumluluğu için düzenle
    return [
        {
            "id": s["recipe"].id,
            "title": s["recipe"].title,
            "instructions": s["recipe"].instructions.split("|"),
            "servings": s["recipe"].servings,
            "ingredients": s["recipe"].ingredients,
            "missing_count": s["missing_count"]
        }
        for s in suggestions
    ]

@app.post("/recipes/{recipe_id}/cook", tags=["Akıllı Analiz"])
def cook_recipe(recipe_id: int, target_servings: int = None, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
        
    # Kullanıcının kilerini getir
    inventory_items = db.query(models.Inventory).filter(models.Inventory.user_id == current_user.id).all()
    
    # Kullanılacak porsiyon sayısına göre malzemeleri oranla
    servings_to_use = target_servings if target_servings and target_servings > 0 else recipe.servings
    scaled_ingredients = utils.scale_recipe(recipe.ingredients, recipe.servings, servings_to_use)
    
    # Kilerdeki ürünleri güncelleyeceğiz
    inventory_dict = {item.name.lower(): item for item in inventory_items if item.name}
    
    deducted_items = []
    
    for scaled_ing in scaled_ingredients:
        name_lower = scaled_ing["name"].lower()
        if name_lower in inventory_dict:
            inv_item = inventory_dict[name_lower]
            # Miktarı düşür
            new_amount = inv_item.amount - scaled_ing["scaled_amount"]
            if new_amount < 0:
                new_amount = 0
                
            inv_item.amount = round(new_amount * 100) / 100  # Yuvarlama yapalım, küsuratlar uzamasın
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

# --- AUTH ENDPOINTLERİ ---

@app.post("/auth/register", response_model=schemas.User, tags=["Kimlik Doğrulama"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Email kontrolü
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı")
    
    # Şifreyi hashle ve kaydet
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

@app.post("/auth/login", response_model=schemas.Token, tags=["Kimlik Doğrulama"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Kullanıcıyı bul
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Şifre kontrolü
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token üret
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User, tags=["Kimlik Doğrulama"])
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/recipes/scrape", response_model=schemas.ScrapeResponse, tags=["Scraper"])
def scrape_recipe(request: schemas.ScrapeRequest):
    try:
        data = utils_scraper.extract_recipe_from_url(request.url)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Kullanıcı Profil İşlemleri
@app.get("/users/me", response_model=schemas.User, tags=["Kullanıcı"])
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User, tags=["Kullanıcı"])
async def update_user_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
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

@app.get("/utils/allergens", response_model=List[schemas.Allergen], tags=["Araçlar"])
def get_allergens(db: Session = Depends(get_db)):
    return db.query(models.Allergen).all()

@app.get("/utils/preferences", response_model=List[schemas.DietaryPreference], tags=["Araçlar"])
def get_preferences(db: Session = Depends(get_db)):
    return db.query(models.DietaryPreference).all()