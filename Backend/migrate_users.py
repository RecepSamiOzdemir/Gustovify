import os
import sqlite3

db_path = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

def migrate_db():
    if not os.path.exists(db_path):
        print(f"Veritabanı bulunamadı: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add dietary_preferences column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN dietary_preferences VARCHAR")
            print("dietary_preferences kolonu eklendi.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("dietary_preferences kolonu zaten var.")
            else:
                raise e

        # Add allergies column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN allergies VARCHAR")
            print("allergies kolonu eklendi.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("allergies kolonu zaten var.")
            else:
                raise e

        # Add avatar_url column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url VARCHAR")
            print("avatar_url kolonu eklendi.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("avatar_url kolonu zaten var.")
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
