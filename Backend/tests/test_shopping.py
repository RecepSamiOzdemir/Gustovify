from tests.conftest import auth_header, create_authenticated_user


def test_add_shopping_item(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    response = client.post("/shopping-list/", json={
        "name": "Sut",
        "amount": 2,
        "unit": "l"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 2
    assert data["is_checked"] is False


def test_get_shopping_list(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    client.post("/shopping-list/", json={"name": "Sut", "amount": 1, "unit": "l"}, headers=headers)
    client.post("/shopping-list/", json={"name": "Ekmek", "amount": 1, "unit": "pcs"}, headers=headers)

    response = client.get("/shopping-list/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_update_shopping_item_check(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    create_resp = client.post("/shopping-list/", json={"name": "Sut", "amount": 1, "unit": "l"}, headers=headers)
    item_id = create_resp.json()["id"]

    response = client.put(f"/shopping-list/{item_id}", json={"is_checked": True}, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_checked"] is True


def test_delete_shopping_item(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    create_resp = client.post("/shopping-list/", json={"name": "Sut", "amount": 1, "unit": "l"}, headers=headers)
    item_id = create_resp.json()["id"]

    response = client.delete(f"/shopping-list/{item_id}", headers=headers)
    assert response.status_code == 200


def test_bulk_move_to_inventory(client, seed_data):
    token_data = create_authenticated_user(client)
    headers = auth_header(token_data["access_token"])

    # Add items and check them
    resp1 = client.post("/shopping-list/", json={"name": "Sut", "amount": 1, "unit": "l"}, headers=headers)
    resp2 = client.post("/shopping-list/", json={"name": "Ekmek", "amount": 2, "unit": "pcs"}, headers=headers)

    client.put(f"/shopping-list/{resp1.json()['id']}", json={"is_checked": True}, headers=headers)
    client.put(f"/shopping-list/{resp2.json()['id']}", json={"is_checked": True}, headers=headers)

    # Bulk move
    response = client.post("/shopping-list/bulk-move", headers=headers)
    assert response.status_code == 200

    # Shopping list should be empty
    response = client.get("/shopping-list/", headers=headers)
    assert response.json()["total"] == 0

    # Inventory should have 2 items
    response = client.get("/inventory/", headers=headers)
    assert response.json()["total"] == 2
