"""Add user_id column to recipes table."""
import sqlite3


def migrate():
    conn = sqlite3.connect("gustovify.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(recipes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE recipes ADD COLUMN user_id INTEGER REFERENCES users(id)")
        conn.commit()
        print("user_id column added to recipes table.")
    else:
        print("user_id column already exists.")
    conn.close()


if __name__ == "__main__":
    migrate()
