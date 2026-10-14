from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def auth_headers(client):
    client.post("/signup", json={"name": "User", "email": "class@example.com", "password": "StrongPass123"})
    token = client.post("/login", json={"email": "class@example.com", "password": "StrongPass123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def valid_class():
    start = datetime.now(IST) + timedelta(days=2)
    return {"name": "Yoga", "description": "Morning yoga", "instructor": "Priya", "start_time": start.isoformat(), "end_time": (start + timedelta(hours=1)).isoformat(), "capacity": 2}


def test_create_class_and_list(client):
    headers = auth_headers(client)
    response = client.post("/classes", json=valid_class(), headers=headers)
    assert response.status_code == 201
    listed = client.get("/classes")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Yoga"


def test_invalid_capacity(client):
    headers = auth_headers(client)
    data = valid_class()
    data["capacity"] = 0
    assert client.post("/classes", json=data, headers=headers).status_code == 422


def test_end_before_start(client):
    headers = auth_headers(client)
    data = valid_class()
    data["end_time"] = data["start_time"]
    assert client.post("/classes", json=data, headers=headers).status_code == 422


def test_naive_datetime_rejected(client):
    headers = auth_headers(client)
    data = valid_class()
    data["start_time"] = "2030-01-01T07:00:00"
    assert client.post("/classes", json=data, headers=headers).status_code == 422
