import pytest
from fastapi.testclient import TestClient
from src.main import app  

client = TestClient(app)


@pytest.fixture
def user():
    return {
        "email": "test@example.com",
        "product_ids": ["product1", "product2"]
    }


def test_update_order(user):
    order_id = "1d1e45aa-765e-4a25-97e7-92abe0be8352"
    # First create an order to update
    response_create = client.post("/orders/", json=user)
    assert response_create.status_code == 201
    order_data = response_create.json()["data"]

    # Update that order
    update_data = {
        "user_email": "updated@example.com",
        "product_ids": ["product3"]
    }
    response_update = client.put(f"/orders/{order_data['id']}", json=update_data)
    assert response_update.status_code == 200
    assert response_update.json()["data"]["user_email"] == "updated@example.com"
    assert response_update.json()["data"]["product_ids"] == ["product3"]


def test_update_order_user_not_found(user):
    order_id = "1d1e45aa-765e-4a25-97e7-92abe0be8352"
    update_data = {
        "user_email": "nonexisting@example.com",
        "product_ids": ["product3"]
    }
    response_update = client.put(f"/orders/{order_id}", json=update_data)
    assert response_update.status_code == 404
    assert response_update.json()["detail"] == "User not found"


def test_update_order_not_found(user):
    update_data = {
        "user_email": "updated@example.com",
        "product_ids": ["product3"]
    }
    response_update = client.put("/orders/non-existing-id", json=update_data)
    assert response_update.status_code == 404
    assert response_update.json()["detail"] == "Order not found"  
