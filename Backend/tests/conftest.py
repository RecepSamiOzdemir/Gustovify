import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base, get_db
from dependencies import limiter
from main import app

# Disable rate limiting for tests
limiter.enabled = False


# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Get a test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_data(db):
    """Seed test database with categories, allergens, preferences."""
    from seed_data import ALLERGENS, CATEGORIES, PREFERENCES

    for cat_data in CATEGORIES:
        db.add(models.Category(name=cat_data["name"], icon=cat_data["icon"]))
    for name in ALLERGENS:
        db.add(models.Allergen(name=name))
    for name in PREFERENCES:
        db.add(models.DietaryPreference(name=name))
    db.commit()


def register_user(client: TestClient, email: str = "test@example.com", password: str = "TestPass1") -> dict:
    """Helper to register a user and return response data."""
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def login_user(client: TestClient, email: str = "test@example.com", password: str = "TestPass1") -> dict:
    """Helper to login and return token data."""
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()


def auth_header(token: str) -> dict:
    """Helper to create auth header."""
    return {"Authorization": f"Bearer {token}"}


def create_authenticated_user(client: TestClient, email: str = "test@example.com", password: str = "TestPass1") -> dict:
    """Register + login, return token data."""
    register_user(client, email, password)
    return login_user(client, email, password)
