def signup(client, email="user@example.com"):
    return client.post("/signup", json={"name": "Test User", "email": email, "password": "StrongPass123"})


def login(client, email="user@example.com"):
    return client.post("/login", json={"email": email, "password": "StrongPass123"})


def test_signup_success(client):
    response = signup(client)
    assert response.status_code == 201
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_duplicate_signup(client):
    signup(client)
    assert signup(client).status_code == 409


def test_login_success_and_wrong_password(client):
    signup(client)
    assert login(client).status_code == 200
    wrong = client.post("/login", json={"email": "user@example.com", "password": "WrongPassword"})
    assert wrong.status_code == 401


def test_refresh_token(client):
    signup(client)
    tokens = login(client).json()
    response = client.post("/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_access_token_cannot_refresh(client):
    signup(client)
    tokens = login(client).json()
    response = client.post("/refresh", json={"refresh_token": tokens["access_token"]})
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    assert client.post("/classes", json={}).status_code == 401
