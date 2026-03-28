import os
import shutil
import sqlite3

DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'
BACKUP_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify_prefs_backup.db'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None

def migrate_preferences():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    # Backup
    if not os.path.exists(BACKUP_PATH):
        shutil.copyfile(DB_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")

    # We need to use SQLAlchemy for this because we need to populate Many-to-Many interactions easily,
    # or we can do it via raw SQL. Raw SQL is safer for a script that might run before app updates?
    # Actually, SQLAlchemy is safer for logic.

    # But wait, we need to create the new tables first.
    # The app won't create them unless it runs.
    # Let's import models and create tables.
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("Ensured new tables (Allergens, DietaryPreferences, User tables) exist.")

    conn = create_connection(DB_PATH)
    cursor = conn.cursor()

    # Pre-populate some standard data if empty
    defaults_allergens = ["Gluten", "Peanut", "Dairy", "Egg", "Soy", "Fish", "Shellfish", "Tree Nuts"]
    defaults_preferences = ["Vegan", "Vegetarian", "Pescatarian", "Keto", "Paleo", "Gluten-Free", "Halal"]

    print("Populating default Allergens...")
    for name in defaults_allergens:
        try:
            cursor.execute("INSERT INTO allergens (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError:
            pass # Already exists

    print("Populating default Preferences...")
    for name in defaults_preferences:
        try:
            cursor.execute("INSERT INTO dietary_preferences (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError:
            pass # Already exists

    conn.commit()

    # Get Master IDs map
    cursor.execute("SELECT id, name FROM allergens")
    allergen_map = {row[1].lower(): row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT id, name FROM dietary_preferences")
    preference_map = {row[1].lower(): row[0] for row in cursor.fetchall()}

    # Migrate Users
    # We need to check if columns exist first. If they were dropped, we can't migrate.
    # But we didn't drop them yet (in models we removed them from class, but DB still has them unless we use alembic/drop).
    # Since we use `create_all`, it doesn't drop columns. So the old columns `allergies` and `dietary_preferences` should still be there
    # IF they were created by previous `migrate_v2` or `models.py`.

    # Check if columns exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    has_allergies_col = "allergies" in columns
    has_prefs_col = "dietary_preferences" in columns

    if has_allergies_col or has_prefs_col:
        print("Migrating user data...")
        try:
            cursor.execute("SELECT id, allergies, dietary_preferences FROM users")
            users = cursor.fetchall()

            for u in users:
                u_id, u_allergies, u_prefs = u

                # Migrate Allergies
                if u_allergies and has_allergies_col:
                    items = [x.strip() for x in u_allergies.split(',') if x.strip()]
                    for item in items:
                        # Find or Create
                        a_id = allergen_map.get(item.lower())
                        if not a_id:
                            # Create new
                            cursor.execute("INSERT INTO allergens (name) VALUES (?)", (item.title(),))
                            a_id = cursor.lastrowid
                            allergen_map[item.lower()] = a_id

                        # Link
                        try:
                            cursor.execute("INSERT INTO user_allergens (user_id, allergen_id) VALUES (?, ?)", (u_id, a_id))
                        except sqlite3.IntegrityError:
                            pass

                # Migrate Preferences
                if u_prefs and has_prefs_col:
                    items = [x.strip() for x in u_prefs.split(',') if x.strip()]
                    for item in items:
                         # Find or Create
                        p_id = preference_map.get(item.lower())
                        if not p_id:
                            # Create new
                            cursor.execute("INSERT INTO dietary_preferences (name) VALUES (?)", (item.title(),))
                            p_id = cursor.lastrowid
                            preference_map[item.lower()] = p_id

                        # Link
                        try:
                            cursor.execute("INSERT INTO user_preferences (user_id, preference_id) VALUES (?, ?)", (u_id, p_id))
                        except sqlite3.IntegrityError:
                            pass

            print(f"Migrated data for {len(users)} users.")
        except Exception as e:
            print(f"Error migrating data: {e}")
    else:
        print("Old columns not found, skipping data migration.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_preferences()
