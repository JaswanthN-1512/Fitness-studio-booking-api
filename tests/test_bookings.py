from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def register_and_token(client, email):
    client.post("/signup", json={"name": email.split("@")[0], "email": email, "password": "StrongPass123"})
    return client.post("/login", json={"email": email, "password": "StrongPass123"}).json()["access_token"]


def make_class(client, token, capacity=2):
    start = datetime.now(IST) + timedelta(days=2)
    data = {"name": "HIIT", "description": "Training", "instructor": "Rahul", "start_time": start.isoformat(), "end_time": (start + timedelta(hours=1)).isoformat(), "capacity": capacity}
    return client.post("/classes", json=data, headers={"Authorization": f"Bearer {token}"}).json()


def test_successful_booking_and_duplicate(client):
    token = register_and_token(client, "booker@example.com")
    cls = make_class(client, token)
    headers = {"Authorization": f"Bearer {token}"}
    first = client.post("/book", json={"class_id": cls["id"]}, headers=headers)
    assert first.status_code == 201
    assert first.json()["class_name"] == "HIIT"
    duplicate = client.post("/book", json={"class_id": cls["id"]}, headers=headers)
    assert duplicate.status_code == 409


def test_full_class_rejected_and_slots_do_not_go_negative(client):
    token_a = register_and_token(client, "a@example.com")
    cls = make_class(client, token_a, capacity=2)
    client.post("/book", json={"class_id": cls["id"]}, headers={"Authorization": f"Bearer {token_a}"})
    token_b = register_and_token(client, "b@example.com")
    client.post("/book", json={"class_id": cls["id"]}, headers={"Authorization": f"Bearer {token_b}"})
    token_c = register_and_token(client, "c@example.com")
    third = client.post("/book", json={"class_id": cls["id"]}, headers={"Authorization": f"Bearer {token_c}"})
    assert third.status_code == 409
    classes = client.get("/classes").json()
    matching = next(x for x in classes if x["id"] == cls["id"])
    assert matching["available_slots"] == 0


def test_user_only_sees_own_bookings(client):
    token_a = register_and_token(client, "owner@example.com")
    cls = make_class(client, token_a)
    client.post("/book", json={"class_id": cls["id"]}, headers={"Authorization": f"Bearer {token_a}"})
    token_b = register_and_token(client, "other@example.com")
    response = client.get("/bookings", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    assert response.json() == []
