from tests.conftest import auth_header, create_authenticated_user, login_user, register_user


def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "StrongPass1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email(client):
    register_user(client, "dup@example.com")
    response = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "StrongPass1"
    })
    assert response.status_code == 400


def test_register_weak_password_short(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Ab1"
    })
    assert response.status_code == 422


def test_register_weak_password_no_uppercase(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "weakpass1"
    })
    assert response.status_code == 422


def test_register_weak_password_no_digit(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "WeakPasss"
    })
    assert response.status_code == 422


def test_login_success(client):
    register_user(client)
    token_data = login_user(client)
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_wrong_password(client):
    register_user(client)
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "WrongPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "TestPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_refresh_token(client):
    token_data = create_authenticated_user(client)
    response = client.post("/auth/refresh", json={
        "refresh_token": token_data["refresh_token"]
    })
    assert response.status_code == 200
    new_data = response.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != token_data["refresh_token"]


def test_refresh_invalid_token(client):
    response = client.post("/auth/refresh", json={
        "refresh_token": "invalid-token"
    })
    assert response.status_code == 401


def test_logout(client):
    token_data = create_authenticated_user(client)
    response = client.post("/auth/logout", json={
        "refresh_token": token_data["refresh_token"]
    })
    assert response.status_code == 200

    # After logout, refresh should fail
    response = client.post("/auth/refresh", json={
        "refresh_token": token_data["refresh_token"]
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client):
    token_data = create_authenticated_user(client)
    response = client.get("/users/me", headers=auth_header(token_data["access_token"]))
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
