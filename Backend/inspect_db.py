import models
from database import SessionLocal

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
