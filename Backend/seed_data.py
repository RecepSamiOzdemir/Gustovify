import models
from database import SessionLocal

# Data Sets (Turkish)
CATEGORIES = [
    {"name": "Sebze", "icon": "🥦"},
    {"name": "Meyve", "icon": "🍎"},
    {"name": "Et & Kümes Hayvanları", "icon": "🥩"},
    {"name": "Süt Ürünleri", "icon": "🥛"},
    {"name": "Bakliyat", "icon": "🫘"},
    {"name": "Tahıl & Ekmek", "icon": "🍞"},
    {"name": "Baharat & Çeşni", "icon": "🧂"},
    {"name": "İçecek", "icon": "🥤"},
    {"name": "Deniz Ürünleri", "icon": "🐟"},
    {"name": "Atıştırmalık", "icon": "🍿"},
    {"name": "Tatlı & Şekerleme", "icon": "🍬"},
    {"name": "Sos & Yağ", "icon": "🥫"},
    {"name": "Diğer", "icon": "📦"}
]

ALLERGENS = [
    "Gluten",
    "Yer Fıstığı",
    "Süt",
    "Yumurta",
    "Soya",
    "Balık",
    "Kabuklu Deniz Ürünleri",
    "Kuruyemiş",
    "Susam",
    "Hardal",
    "Kereviz"
]

PREFERENCES = [
    "Vegan",
    "Vejetaryen",
    "Pesketaryen",
    "Ketojenik (Keto)",
    "Paleo",
    "Glutensiz",
    "Helal",
    "Düşük Karbonhidrat",
    "Şekersiz"
]

def seed_database():
    db = SessionLocal()

    print("Seeding Categories...")
    for cat_data in CATEGORIES:
        exists = db.query(models.Category).filter(models.Category.name == cat_data["name"]).first()
        if not exists:
            # Check if name exists with different case?
            # For now simplified
            cat = models.Category(name=cat_data["name"], icon=cat_data["icon"])
            db.add(cat)
            print(f"Added Category: {cat_data['name']}")
        else:
            # Update icon if missing
            if not exists.icon:
                exists.icon = cat_data["icon"]
                print(f"Updated Icon for: {cat_data['name']}")

    print("\nSeeding Allergens...")
    for name in ALLERGENS:
        exists = db.query(models.Allergen).filter(models.Allergen.name == name).first()
        if not exists:
            allergen = models.Allergen(name=name)
            db.add(allergen)
            print(f"Added Allergen: {name}")

    print("\nSeeding Dietary Preferences...")
    for name in PREFERENCES:
        exists = db.query(models.DietaryPreference).filter(models.DietaryPreference.name == name).first()
        if not exists:
            pref = models.DietaryPreference(name=name)
            db.add(pref)
            print(f"Added Preference: {name}")

    db.commit()
    db.close()
    print("\nSeeding Complete! 🌱")

if __name__ == "__main__":
    seed_database()
