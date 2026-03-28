import sqlite3

db_path = 'c:\\Users\\recep\\Gustovify\\Backend\\gustovify.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Silme sırası önemli: Önce ilişkili tablolar (Inventory), sonra ana tablo (User)
    cursor.execute("DELETE FROM inventory")
    print("Kiler (Inventory) tablosu temizlendi.")

    cursor.execute("DELETE FROM users")
    print("Kullanıcılar (Users) tablosu temizlendi.")

    conn.commit()
    conn.close()
    print("Veritabanı kullanıcı kayıtları başarıyla sıfırlandı.")
except Exception as e:
    print(f"Hata oluştu: {e}")
