# 'create_all' ifadesini buradan siliyoruz
from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Geri kalan kısım aynı kalabilir
SQLALCHEMY_DATABASE_URL = "sqlite:///./gustovify.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı bağlantısı için yardımcı fonksiyon (Dependency)
# Dependency Injection için burada tanımlanması en sağlıklısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()