import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_pantry_flow():
    # 1. Register
    email = "test@example.com"
    password = "password123"
    print(f"Registering user {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if resp.status_code == 200:
        print("Registration successful.")
    elif resp.status_code == 400 and "zaten kayıtlı" in resp.text:
        print("User already exists, proceeding to login.")
    else:
        print(f"Registration failed: {resp.text}")
        sys.exit(1)

    # 2. Login
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        sys.exit(1)
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 3. Add Item
    item = {
        "name": "Test Domates",
        "amount": 5.0,
        "unit": "kg",
        "category": "Sebze",
        "expiry_date": "2024-12-31"
    }
    print("Adding item to pantry...")
    resp = requests.post(f"{BASE_URL}/inventory/", json=item, headers=headers)
    if resp.status_code != 200:
        print(f"Add item failed: {resp.text}")
        sys.exit(1)
    item_id = resp.json()["id"]
    print(f"Item added with ID: {item_id}")

    # 4. Get Inventory
    print("Fetching inventory...")
    resp = requests.get(f"{BASE_URL}/inventory/", headers=headers)
    if resp.status_code != 200:
        print(f"Get inventory failed: {resp.text}")
        sys.exit(1)
    
    items = resp.json()
    print(f"Inventory items: {items}")
    
    found = False
    for i in items:
        if i["name"] == "Test Domates" and i["category"] == "Sebze":
            found = True
            break
    
    if found:
        print("SUCCESS: Item found in inventory with correct details.")
    else:
        print("FAILURE: Item not found in inventory.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_pantry_flow()
    except Exception as e:
        print(f"Test failed with exception: {e}")
        sys.exit(1)
