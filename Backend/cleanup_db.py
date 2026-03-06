import sqlite3

DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete duplicate English Allergens (1-8)
print("Deleting English Allergens (1-8)...")
cursor.execute("DELETE FROM allergens WHERE id BETWEEN 1 AND 8")

# Delete duplicate English and Garbage Preferences (1-10)
print("Deleting English/Garbage Preferences (1-10)...")
cursor.execute("DELETE FROM dietary_preferences WHERE id BETWEEN 1 AND 10")

# Also delete from association tables to avoid orphan references
print("Cleaning up association tables...")
cursor.execute("DELETE FROM user_allergens WHERE allergen_id BETWEEN 1 AND 8")
cursor.execute("DELETE FROM user_preferences WHERE preference_id BETWEEN 1 AND 10")

conn.commit()
print("Cleanup complete.")

print("\n--- NEW ALLERGENS ---")
cursor.execute("SELECT id, name FROM allergens")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n--- NEW PREFERENCES ---")
cursor.execute("SELECT id, name FROM dietary_preferences")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
