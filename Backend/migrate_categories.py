import sqlite3
import os
import shutil

DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'
BACKUP_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify_cats_backup.db'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None

def migrate_categories():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    # Backup
    if not os.path.exists(BACKUP_PATH):
        shutil.copyfile(DB_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")

    # Ensure tables exist
    from database import engine, Base
    import models
    Base.metadata.create_all(bind=engine)
    print("Ensured Category table exists.")

    conn = create_connection(DB_PATH)
    cursor = conn.cursor()

    # 1. Check if 'category' column exists in 'inventory' and 'master_ingredients'
    # Use PRAGMA to check columns.
    cursor.execute("PRAGMA table_info(master_ingredients)")
    master_cols_info = cursor.fetchall()
    master_cols = [col[1] for col in master_cols_info]
    
    # Check if category_id exists, if not, add it
    if "category_id" not in master_cols:
        print("Adding 'category_id' column to master_ingredients...")
        cursor.execute("ALTER TABLE master_ingredients ADD COLUMN category_id INTEGER REFERENCES categories(id)")
        conn.commit()

    # Access legacy 'category' column if it exists
    has_legacy_cat = "category" in master_cols
    
    master_rows = []
    if has_legacy_cat:
        cursor.execute("SELECT id, category FROM master_ingredients WHERE category IS NOT NULL")
        master_rows = cursor.fetchall()

    cursor.execute("SELECT ingredient_id, category FROM inventory WHERE category IS NOT NULL")
    try:
        inv_rows = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Column 'category' not found in inventory. Skipping inventory scan.")
        inv_rows = []

    # Collect unique categories
    unique_cats = set()
    for row in master_rows:
        if row[1]: unique_cats.add(row[1].strip().title())
    for row in inv_rows:
        if row[1]: unique_cats.add(row[1].strip().title())

    print(f"Found {len(unique_cats)} unique categories: {unique_cats}")

    # Create Categories
    cat_map = {} # name -> id
    for cat_name in unique_cats:
        # Check if exists
        cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
        res = cursor.fetchone()
        if res:
            cat_map[cat_name] = res[0]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat_name,))
            cat_map[cat_name] = cursor.lastrowid
            print(f"Created Category: {cat_name}")

    # Update Master Ingredients
    # First, from its own 'category' column
    count = 0
    for row in master_rows:
        m_id, cat_str = row
        if cat_str:
            clean_name = cat_str.strip().title()
            cat_id = cat_map.get(clean_name)
            if cat_id:
                cursor.execute("UPDATE master_ingredients SET category_id = ? WHERE id = ?", (cat_id, m_id))
                count += 1
    print(f"Updated {count} master ingredients from self.")

    # Second, update Master Ingredients based on Inventory data (if master has no category)
    # Inventory might have 'Sebze' but Master is null. We should promote it to Master.
    count = 0
    for row in inv_rows:
        ing_id, cat_str = row
        if cat_str and ing_id:
            clean_name = cat_str.strip().title()
            cat_id = cat_map.get(clean_name)
            
            # Check if master needs update
            cursor.execute("SELECT category_id FROM master_ingredients WHERE id = ?", (ing_id,))
            res = cursor.fetchone()
            if res and res[0] is None and cat_id:
                 cursor.execute("UPDATE master_ingredients SET category_id = ? WHERE id = ?", (cat_id, ing_id))
                 count += 1
    print(f"Updated {count} master ingredients from inventory data.")

    # We do NOT drop columns here because SQLite makes it hard/risky without full rewrite.
    # We will just ignore the old columns in our code.
    
    conn.commit()
    conn.close()
    print("Category migration complete.")

if __name__ == "__main__":
    migrate_categories()
