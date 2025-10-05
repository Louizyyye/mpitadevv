import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "+254712345678",
        "national_id": "12345678",
        "otp": "1234",
        "occupation": "Tester",
        "password": "TestPass123"
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == payload["email"]
    assert data["data"]["user"]["national_id"] == payload["national_id"]
    assert data["data"]["user"]["otp"] == payload["otp"]
    assert data["data"]["user"]["name"] == payload["name"]
    assert data["data"]["user"]["phone"] == payload["phone"]
