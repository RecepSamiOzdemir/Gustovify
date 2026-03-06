from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

db = SessionLocal()

print("--- ALLERGENS ---")
allergens = db.query(models.Allergen).all()
for a in allergens:
    print(f"{a.id}: {a.name}")

print("\n--- PREFERENCES ---")
prefs = db.query(models.DietaryPreference).all()
for p in prefs:
    print(f"{p.id}: {p.name}")

db.close()
