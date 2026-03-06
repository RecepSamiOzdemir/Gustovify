import sqlite3

db_path = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns = [
    ("user_id", "INTEGER REFERENCES users(id)"),
    ("category", "TEXT"),
    ("expiry_date", "DATE")
]

for col_name, col_type in columns:
    try:
        cursor.execute(f"ALTER TABLE inventory ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name}")
    except Exception as e:
        print(f"Could not add {col_name}: {e}")

conn.commit()
conn.close()
