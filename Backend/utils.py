import math

UNIT_MAPPING = {
    "kg": ["kilogram", "kgs", "kilo"],
    "g": ["gram", "gr", "gms"],
    "l": ["liter", "litre", "lt"],
    "ml": ["milliliter", "cc"],
    "tbsp": ["tablespoon", "yk", "yemek kaşığı", "yemek kasigi", "corba kasigi", "çorba kaşığı"],
    "tsp": ["teaspoon", "tk", "çay kaşığı", "cay kasigi", "tatlı kaşığı", "tatli kasigi"],
    "cup": ["bardak", "su bardağı", "sb"],
    "pcs": ["adet", "tane", "piece", "pieces"],
    "clove": ["diş", "dis"],
    "pinch": ["tutam", "cimdik"],
    "slice": ["dilim"]
}

def normalize_unit(unit_str: str) -> str:
    if not unit_str:
        return unit_str
    
    unit_lower = unit_str.strip().lower()
    
    # Check if key itself
    if unit_lower in UNIT_MAPPING:
        return unit_lower
        
    # Check aliases
    for standard, aliases in UNIT_MAPPING.items():
        if unit_lower in aliases:
            return standard
            
    return unit_lower

def scale_recipe(ingredients, original_servings: int, target_servings: int):
    scaled_ingredients = []
    ratio = target_servings / original_servings

    for ing in ingredients:
        new_amount = ing.amount
        
        # TDD 4.2: Özel birim değilse oranla
        if not ing.is_special_unit:
            new_amount = ing.amount * ratio
            
            # Akıllı Yuvarlama Mantığı (Mühendislik dokunuşu)
            # 0.25'lik dilimlere yuvarlayarak mutfak ölçülerine (çeyrek, yarım) yaklaştırıyoruz
            new_amount = round(new_amount * 4) / 4
            
        scaled_ingredients.append({
            "name": ing.name,
            "original_amount": ing.amount,
            "scaled_amount": new_amount,
            "unit": ing.unit,
            "is_special_unit": ing.is_special_unit
        })
        
    return scaled_ingredients

def check_inventory_for_recipe(recipe_ingredients, inventory_items):
    missing_ingredients = []
    
    # Kilerdeki ürünleri hızlı arama için sözlüğe çevir
    inventory_dict = {item.name.lower(): item.amount for item in inventory_items}
    
    for ing in recipe_ingredients:
        name = ing.name.lower()
        required_amount = ing.amount
        
        # Stokta var mı?
        if name in inventory_dict:
            current_stock = inventory_dict[name]
            if current_stock < required_amount:
                missing_ingredients.append({
                    "name": ing.name,
                    "required": required_amount,
                    "current": current_stock,
                    "missing": required_amount - current_stock,
                    "unit": ing.unit
                })
        else:
            # Stokta hiç yok
            missing_ingredients.append({
                "name": ing.name,
                "required": required_amount,
                "current": 0,
                "missing": required_amount,
                "unit": ing.unit
            })
            
    return missing_ingredients