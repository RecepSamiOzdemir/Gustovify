from datetime import date
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, field_validator

# Generic Paginated Response
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

# TDD 3.5: Malzemenin parametrik objeye dönüştürülmüş taban modeli
class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class MasterIngredientBase(BaseModel):
    name: str
    category_id: Optional[int] = None

class MasterIngredientCreate(MasterIngredientBase):
    pass

class MasterIngredient(MasterIngredientBase):
    id: int
    is_verified: bool
    category: Optional[Category] = None

    class Config:
        from_attributes = True

class IngredientBase(BaseModel):
    amount: float
    unit: str
    is_special_unit: bool = False # TDD 4.2 & 5.6: Orantılanamaz birimler için

class IngredientCreate(IngredientBase):
    name: str # For creation, we still accept name

class Ingredient(IngredientBase):
    id: int
    recipe_id: int
    ingredient_id: int
    name: Optional[str] = None # Populated manually or via validator

    class Config:
        from_attributes = True

# TDD 2.3: Reçete veri seti yapısı
class RecipeBase(BaseModel):
    title: str
    instructions: List[str]
    servings: int

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]

class Recipe(RecipeBase):
    id: int
    user_id: Optional[int] = None
    image_url: Optional[str] = None
    ingredients: List[Ingredient]

    @field_validator('instructions', mode='before')
    @classmethod
    def parse_instructions_from_db(cls, v):
        if isinstance(v, list):
            return v
        if not v:
            return []
        try:
            import json
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return [s.strip() for s in v.split("|") if s.strip()]

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    amount: float
    unit: str
    expiry_date: Optional[date] = None

class InventoryCreate(InventoryBase):
    name: str # User inputs name
    category: Optional[str] = None # Input for creation logic (to find/create category)

class InventoryUpdate(BaseModel):
    amount: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None # Can update master link via logic if needed
    expiry_date: Optional[date] = None

class IngredientUpdate(BaseModel):
    id: Optional[int] = None # Varsa güncelle, yoksa ekle
    name: str
    amount: float
    unit: str
    is_special_unit: bool = False

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    instructions: Optional[List[str]] = None
    servings: Optional[int] = None
    ingredients: Optional[List[IngredientUpdate]] = None

class Inventory(InventoryBase):
    id: int
    user_id: int
    ingredient_id: int
    name: Optional[str] = None # Populated manually

    class Config:
        from_attributes = True

class ShoppingListItemBase(BaseModel):
    amount: float
    unit: str
    is_checked: bool = False

class ShoppingListItemCreate(ShoppingListItemBase):
    name: str
    category: Optional[str] = None

class ShoppingListItemUpdate(BaseModel):
    amount: Optional[float] = None
    unit: Optional[str] = None
    is_checked: Optional[bool] = None
    category: Optional[str] = None

class ShoppingListItem(ShoppingListItemBase):
    id: int
    user_id: int
    ingredient_id: int
    name: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True

class AllergenBase(BaseModel):
    name: str

class Allergen(AllergenBase):
    id: int
    class Config:
        from_attributes = True

class DietaryPreferenceBase(BaseModel):
    name: str

class DietaryPreference(DietaryPreferenceBase):
    id: int
    class Config:
        from_attributes = True

# Kullanıcı işlemleri için şemalar
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    allergen_ids: Optional[List[int]] = []
    preference_ids: Optional[List[int]] = []

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not any(c.isupper() for c in v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not any(c.isdigit() for c in v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v

class UserUpdate(BaseModel):
    password: Optional[str] = None
    full_name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    cooking_level: Optional[str] = None
    avatar_url: Optional[str] = None
    allergen_ids: Optional[List[int]] = None
    preference_ids: Optional[List[int]] = None

class User(UserBase):
    id: int
    is_active: bool
    full_name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    cooking_level: Optional[str] = None
    avatar_url: Optional[str] = None

    # Relationships
    related_allergens: List[Allergen] = []
    related_preferences: List[DietaryPreference] = []

    class Config:
        from_attributes = True

# Token yanıtı için şemalar
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    title: str
    ingredients: List[IngredientCreate]
    instructions: List[str]
    servings: int
    image_url: Optional[str] = None
    source_url: Optional[str] = None
