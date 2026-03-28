from tests.conftest import auth_header, create_authenticated_user


def test_add_inventory_item(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.post("/inventory/", json={
        "name": "Un",
        "amount": 2.5,
        "unit": "kg"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 2.5
    assert data["unit"] == "kg"


def test_get_inventory(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    client.post("/inventory/", json={"name": "Un", "amount": 1, "unit": "kg"}, headers=headers)
    client.post("/inventory/", json={"name": "Seker", "amount": 500, "unit": "g"}, headers=headers)

    response = client.get("/inventory/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_duplicate_inventory_item_accumulates(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    client.post("/inventory/", json={"name": "Un", "amount": 1, "unit": "kg"}, headers=headers)
    client.post("/inventory/", json={"name": "Un", "amount": 0.5, "unit": "kg"}, headers=headers)

    response = client.get("/inventory/", headers=headers)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["amount"] == 1.5


def test_update_inventory_item(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    create_resp = client.post("/inventory/", json={"name": "Sut", "amount": 1, "unit": "l"}, headers=headers)
    item_id = create_resp.json()["id"]

    response = client.put(f"/inventory/{item_id}", json={"amount": 0.5}, headers=headers)
    assert response.status_code == 200
    assert response.json()["amount"] == 0.5


def test_delete_inventory_item(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    create_resp = client.post("/inventory/", json={"name": "Tuz", "amount": 1, "unit": "kg"}, headers=headers)
    item_id = create_resp.json()["id"]

    response = client.delete(f"/inventory/{item_id}", headers=headers)
    assert response.status_code == 200

    response = client.get("/inventory/", headers=headers)
    assert response.json()["total"] == 0


def test_inventory_isolation_between_users(client, seed_data):
    user1_data = create_authenticated_user(client, "user1@test.com")
    headers1 = auth_header(user1_data["access_token"])
    client.post("/inventory/", json={"name": "Un", "amount": 1, "unit": "kg"}, headers=headers1)

    user2_data = create_authenticated_user(client, "user2@test.com")
    headers2 = auth_header(user2_data["access_token"])
    response = client.get("/inventory/", headers=headers2)
    assert response.json()["total"] == 0


def test_inventory_with_expiry_date(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.post("/inventory/", json={
        "name": "Sut",
        "amount": 1,
        "unit": "l",
        "expiry_date": "2026-04-15"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["expiry_date"] == "2026-04-15"
