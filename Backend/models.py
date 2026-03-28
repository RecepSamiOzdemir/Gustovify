from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base

# Association Tables
user_allergens = Table(
    'user_allergens', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('allergen_id', Integer, ForeignKey('allergens.id'))
)

user_preferences = Table(
    'user_preferences', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('preference_id', Integer, ForeignKey('dietary_preferences.id'))
)

class Allergen(Base):
    __tablename__ = "allergens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class DietaryPreference(Base):
    __tablename__ = "dietary_preferences"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    icon = Column(String, nullable=True) # Emoji or icon name

class MasterIngredient(Base):
    __tablename__ = "master_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_verified = Column(Boolean, default=False)

    category = relationship("Category")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    instructions = Column(String)  # JSON string
    servings = Column(Integer)
    image_url = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    owner = relationship("User")

class RecipeIngredient(Base): # Renamed from Ingredient
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    # name removed, replaced by ingredient_id
    amount = Column(Float)
    unit = Column(String)
    is_special_unit = Column(Boolean, default=False) # TDD 4.2 [cite: 56]

    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    ingredient_id = Column(Integer, ForeignKey("master_ingredients.id"))

    recipe = relationship("Recipe", back_populates="ingredients")
    master_ingredient = relationship("MasterIngredient")

    @property
    def name(self):
        return self.master_ingredient.name if self.master_ingredient else None

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    unit = Column(String)
    expiry_date = Column(Date, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient_id = Column(Integer, ForeignKey("master_ingredients.id"))

    user = relationship("User", back_populates="inventory_items")
    master_ingredient = relationship("MasterIngredient")

    @property
    def name(self):
        return self.master_ingredient.name if self.master_ingredient else None

    @property
    def category(self):
        return self.master_ingredient.category.name if self.master_ingredient and self.master_ingredient.category else None

class ShoppingListItem(Base):
    __tablename__ = "shopping_list"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    unit = Column(String)
    is_checked = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient_id = Column(Integer, ForeignKey("master_ingredients.id"))

    user = relationship("User", back_populates="shopping_list")
    master_ingredient = relationship("MasterIngredient")

    @property
    def name(self):
        return self.master_ingredient.name if self.master_ingredient else None

    @property
    def category(self):
        return self.master_ingredient.category.name if self.master_ingredient and self.master_ingredient.category else None


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    full_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    dietary_preferences = Column(String, nullable=True) # JSON or CSV string
    allergies = Column(String, nullable=True) # JSON or CSV string
    cooking_level = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    inventory_items = relationship("Inventory", back_populates="user")
    shopping_list = relationship("ShoppingListItem", back_populates="user")
    related_allergens = relationship("Allergen", secondary=user_allergens)
    related_preferences = relationship("DietaryPreference", secondary=user_preferences)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(Date)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User")
