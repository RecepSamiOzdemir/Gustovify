import sqlite3
import os

db_path = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

def migrate_db():
    if not os.path.exists(db_path):
        print(f"Veritabanı bulunamadı: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns = [
        ("full_name", "VARCHAR"),
        ("city", "VARCHAR"),
        ("cooking_level", "VARCHAR"),
        ("age", "INTEGER"),
        ("gender", "VARCHAR")
    ]

    try:
        for col_name, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"{col_name} kolonu eklendi.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"{col_name} kolonu zaten var.")
                else:
                    raise e

        conn.commit()
        print("Migrasyon tamamlandı.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
