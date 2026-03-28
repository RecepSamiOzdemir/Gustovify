"""Add image_url column to recipes table."""
import sqlite3


def migrate():
    conn = sqlite3.connect("gustovify.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(recipes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "image_url" not in columns:
        cursor.execute("ALTER TABLE recipes ADD COLUMN image_url TEXT")
        conn.commit()
        print("image_url column added to recipes table.")
    else:
        print("image_url column already exists.")
    conn.close()


if __name__ == "__main__":
    migrate()
