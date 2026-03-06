import sqlite3
import os
import shutil

# Paths
DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'
BACKUP_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify_backup.db'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None

def fetch_all(cursor, table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        # Get column names
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Could not read {table_name}: {e}")
        return []

def migrate_data():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    # Backup existing database
    if not os.path.exists(BACKUP_PATH):
        shutil.copyfile(DB_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    else:
        print(f"Backup already exists at {BACKUP_PATH}, using it as source.")

    conn = create_connection(BACKUP_PATH) # Read from Backup to be safe
    cursor = conn.cursor()

    print("Reading existing data...")
    recipes = fetch_all(cursor, "recipes")
    ingredients = fetch_all(cursor, "ingredients")
    inventory = fetch_all(cursor, "inventory")
    users = fetch_all(cursor, "users")
    
    conn.close()
    
    # Logic to normalize ingredients
    print("Normalizing ingredients...")
    # Clean names
    all_names = set()
    for row in ingredients:
        if row.get('name'):
            all_names.add(row['name'].strip().lower().title())
    
    for row in inventory:
        if row.get('name'):
            all_names.add(row['name'].strip().lower().title())
    
    master_map = {} # name -> id (will be assigned later)
    master_list = []
    
    for idx, name in enumerate(sorted(all_names), 1):
        master_map[name.lower()] = idx
        master_list.append({'id': idx, 'name': name, 'is_verified': False})
    
    print(f"Found {len(master_list)} unique master ingredients.")

    # Recreate DB
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Old DB removed. Creating new one...")
        except PermissionError:
             print("Error: Could not remove old DB. Make sure no other process is using it.")
             return

    # Create tables via SQLAlchemy
    from database import engine, Base
    import models 
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    new_conn = create_connection(DB_PATH)
    new_cursor = new_conn.cursor()
    
    # Insert Users
    if users:
        print(f"Restoring {len(users)} users...")
        for user in users:
            # Dynamically build insert query based on available columns
            cols = ', '.join(user.keys())
            placeholders = ', '.join(['?'] * len(user))
            sql = f"INSERT INTO users ({cols}) VALUES ({placeholders})"
            new_cursor.execute(sql, list(user.values()))

    # Insert Master Ingredients
    if master_list:
        print(f"Inserting {len(master_list)} master ingredients...")
        for m in master_list:
             new_cursor.execute("INSERT INTO master_ingredients (id, name, is_verified) VALUES (?, ?, ?)", 
                                (m['id'], m['name'], m['is_verified']))

    # Insert Recipes
    if recipes:
        print(f"Restoring {len(recipes)} recipes...")
        for r in recipes:
             cols = ', '.join(r.keys())
             placeholders = ', '.join(['?'] * len(r))
             sql = f"INSERT INTO recipes ({cols}) VALUES ({placeholders})"
             new_cursor.execute(sql, list(r.values()))

    # Insert Recipe Ingredients
    if ingredients:
        print(f"Restoring {len(ingredients)} recipe ingredients...")
        count = 0
        for i in ingredients:
            name = i.get('name', '').strip().lower()
            m_id = master_map.get(name)
            if m_id:
                new_cursor.execute("""
                    INSERT INTO recipe_ingredients (amount, unit, is_special_unit, recipe_id, ingredient_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (i['amount'], i['unit'], i['is_special_unit'], i['recipe_id'], m_id))
                count += 1
        print(f"Inserted {count} recipe ingredients.")

    # Insert Inventory
    if inventory:
        print(f"Restoring {len(inventory)} inventory items...")
        count = 0
        for i in inventory:
            name = i.get('name', '').strip().lower()
            m_id = master_map.get(name)
            if m_id:
                # Check for category if exists in old data
                cat = i.get('category')
                exp = i.get('expiry_date')
                user_id = i['user_id']
                
                new_cursor.execute("""
                    INSERT INTO inventory (amount, unit, category, expiry_date, user_id, ingredient_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (i['amount'], i['unit'], cat, exp, user_id, m_id))
                count += 1
        print(f"Inserted {count} inventory items.")

    new_conn.commit()
    new_conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_data()
