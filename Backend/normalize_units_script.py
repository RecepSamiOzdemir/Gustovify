import os
import sqlite3

import utils  # Import our new normalization logic

DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None

def normalize_existing_data():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = create_connection(DB_PATH)
    cursor = conn.cursor()

    print("Normalizing recipe ingredients...")
    cursor.execute("SELECT id, unit FROM recipe_ingredients")
    rows = cursor.fetchall()

    count = 0
    for row in rows:
        item_id, unit = row
        normalized = utils.normalize_unit(unit)
        if normalized != unit:
            cursor.execute("UPDATE recipe_ingredients SET unit = ? WHERE id = ?", (normalized, item_id))
            count += 1
            print(f"Recipe Ingredient {item_id}: '{unit}' -> '{normalized}'")

    print(f"Updated {count} recipe ingredients.")

    print("Normalizing inventory items...")
    cursor.execute("SELECT id, unit FROM inventory")
    rows = cursor.fetchall()

    count = 0
    for row in rows:
        item_id, unit = row
        normalized = utils.normalize_unit(unit)
        if normalized != unit:
            cursor.execute("UPDATE inventory SET unit = ? WHERE id = ?", (normalized, item_id))
            count += 1
            print(f"Inventory Item {item_id}: '{unit}' -> '{normalized}'")

    print(f"Updated {count} inventory items.")

    conn.commit()
    conn.close()
    print("Normalization complete.")

if __name__ == "__main__":
    normalize_existing_data()
