import sqlite3

DB_PATH = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- ALLERGENS ---")
cursor.execute("SELECT id, name FROM allergens")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n--- PREFERENCES ---")
cursor.execute("SELECT id, name FROM dietary_preferences")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
