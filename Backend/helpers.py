import json

from sqlalchemy.orm import Session

import models


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
