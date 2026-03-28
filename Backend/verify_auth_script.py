from datetime import timedelta

from jose import jwt

from auth import ALGORITHM, SECRET_KEY, create_access_token, get_password_hash, verify_password


def test_auth_flow():
    print("--- Authentication Verification Started ---")

    # 1. Test Password Hashing
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    print(f"[OK] Password hashed: {hashed[:10]}...")

    # 2. Test Password Verification
    assert verify_password(password, hashed) == True
    print("[OK] Password verification successful")

    assert verify_password("wrongpassword", hashed) == False
    print("[OK] Wrong password correctly rejected")

    # 3. Test Token Generation
    data = {"sub": "test@example.com"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=15))
    print(f"[OK] Token generated: {token[:10]}...")

    # 4. Test Token Decoding
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    print("[OK] Token decoded successfully with correct payload")

    print("--- Authentication Verification Completed Successfully ---")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"[FAIL] usage error: {e}")
        exit(1)
