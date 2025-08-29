from src.auth import hash_password, verify_password


def test_hash_and_verify_password():
    password = 'mysecret123'
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(hashed, password)
    assert not verify_password(hashed, 'wrongpass')
