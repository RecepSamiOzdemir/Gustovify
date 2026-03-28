from tests.conftest import auth_header, create_authenticated_user


def test_create_recipe(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.post("/recipes/", json={
        "title": "Test Tarif",
        "instructions": ["Adim 1", "Adim 2"],
        "servings": 4,
        "ingredients": [
            {"name": "Un", "amount": 2, "unit": "cup", "is_special_unit": False},
            {"name": "Seker", "amount": 1, "unit": "cup", "is_special_unit": False}
        ]
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Tarif"
    assert len(data["ingredients"]) == 2
    assert data["servings"] == 4


def test_get_recipes(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Create a recipe first
    client.post("/recipes/", json={
        "title": "Tarif 1",
        "instructions": ["Adim 1"],
        "servings": 2,
        "ingredients": [{"name": "Tuz", "amount": 1, "unit": "tsp", "is_special_unit": False}]
    }, headers=headers)

    response = client.get("/recipes/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Tarif 1"


def test_recipe_ownership(client, seed_data):
    # User 1 creates a recipe
    user1_data = create_authenticated_user(client, "user1@test.com")
    headers1 = auth_header(user1_data["access_token"])
    client.post("/recipes/", json={
        "title": "User1 Tarif",
        "instructions": ["Adim 1"],
        "servings": 2,
        "ingredients": [{"name": "Tuz", "amount": 1, "unit": "tsp", "is_special_unit": False}]
    }, headers=headers1)

    # User 2 should not see User 1's recipes
    user2_data = create_authenticated_user(client, "user2@test.com")
    headers2 = auth_header(user2_data["access_token"])
    response = client.get("/recipes/", headers=headers2)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_update_recipe(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Create recipe
    create_resp = client.post("/recipes/", json={
        "title": "Eski Isim",
        "instructions": ["Adim 1"],
        "servings": 2,
        "ingredients": [{"name": "Un", "amount": 1, "unit": "cup", "is_special_unit": False}]
    }, headers=headers)
    recipe_id = create_resp.json()["id"]

    # Update recipe
    response = client.put(f"/recipes/{recipe_id}", json={
        "title": "Yeni Isim",
        "servings": 4
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Yeni Isim"
    assert response.json()["servings"] == 4


def test_delete_recipe(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Create recipe
    create_resp = client.post("/recipes/", json={
        "title": "Silinecek",
        "instructions": ["Adim 1"],
        "servings": 2,
        "ingredients": [{"name": "Un", "amount": 1, "unit": "cup", "is_special_unit": False}]
    }, headers=headers)
    recipe_id = create_resp.json()["id"]

    # Delete recipe
    response = client.delete(f"/recipes/{recipe_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    response = client.get("/recipes/", headers=headers)
    assert response.json()["total"] == 0


def test_delete_other_users_recipe(client, seed_data):
    # User 1 creates recipe
    user1_data = create_authenticated_user(client, "user1@test.com")
    headers1 = auth_header(user1_data["access_token"])
    create_resp = client.post("/recipes/", json={
        "title": "User1 Tarif",
        "instructions": ["Adim 1"],
        "servings": 2,
        "ingredients": [{"name": "Tuz", "amount": 1, "unit": "tsp", "is_special_unit": False}]
    }, headers=headers1)
    recipe_id = create_resp.json()["id"]

    # User 2 tries to delete
    user2_data = create_authenticated_user(client, "user2@test.com")
    headers2 = auth_header(user2_data["access_token"])
    response = client.delete(f"/recipes/{recipe_id}", headers=headers2)
    assert response.status_code == 404


def test_scale_recipe(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Create recipe with 4 servings
    create_resp = client.post("/recipes/", json={
        "title": "Kek",
        "instructions": ["Karistir", "Pisir"],
        "servings": 4,
        "ingredients": [
            {"name": "Un", "amount": 2, "unit": "cup", "is_special_unit": False},
            {"name": "Tuz", "amount": 1, "unit": "pinch", "is_special_unit": True}
        ]
    }, headers=headers)
    recipe_id = create_resp.json()["id"]

    # Scale to 8 servings
    response = client.get(f"/recipes/{recipe_id}/scale/8", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["target_servings"] == 8
    assert data["original_servings"] == 4


def test_create_recipe_without_auth(client):
    response = client.post("/recipes/", json={
        "title": "Test",
        "instructions": ["Step 1"],
        "servings": 2,
        "ingredients": []
    })
    assert response.status_code == 401
