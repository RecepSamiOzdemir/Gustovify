from tests.conftest import auth_header, create_authenticated_user


def test_get_current_user(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_update_profile(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.put("/users/me", json={
        "full_name": "Test User",
        "city": "Istanbul",
        "age": 25,
        "cooking_level": "intermediate"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["city"] == "Istanbul"
    assert data["age"] == 25
    assert data["cooking_level"] == "intermediate"


def test_update_allergens(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.put("/users/me", json={
        "allergen_ids": [1, 2]
    }, headers=headers)
    assert response.status_code == 200
    allergens = response.json()["related_allergens"]
    assert len(allergens) == 2


def test_update_preferences(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.put("/users/me", json={
        "preference_ids": [1]
    }, headers=headers)
    assert response.status_code == 200
    prefs = response.json()["related_preferences"]
    assert len(prefs) == 1


def test_change_password(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Change password
    response = client.put("/users/me", json={"password": "NewPass123"}, headers=headers)
    assert response.status_code == 200

    # Login with new password
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "NewPass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
