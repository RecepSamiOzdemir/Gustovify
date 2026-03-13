"""Convert pipe-delimited instructions to JSON format."""
import sqlite3
import json


def migrate():
    conn = sqlite3.connect("gustovify.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, instructions FROM recipes")
    rows = cursor.fetchall()
    migrated = 0
    for row_id, instructions in rows:
        if instructions and not instructions.startswith("["):
            steps = [s.strip() for s in instructions.split("|") if s.strip()]
            cursor.execute(
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (json.dumps(steps, ensure_ascii=False), row_id)
            )
            migrated += 1
    conn.commit()
    print(f"Migrated {migrated}/{len(rows)} recipes to JSON instructions.")
    conn.close()


if __name__ == "__main__":
    migrate()
