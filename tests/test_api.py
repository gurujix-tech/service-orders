"""API tests for service-orders.

Run from the service-orders directory with the venv active:
  pytest -q
"""

from fastapi.testclient import TestClient

from app.main import _orders, app

client = TestClient(app)


def setup_function() -> None:
    """Isolate tests: clear in-memory store before each test."""
    _orders.clear()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_create_and_get_order() -> None:
    create = client.post(
        "/orders",
        json={
            "product_id": "sku-tea-001",
            "quantity": 2,
            "customer_email": "guest@gurujix.com",
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["product_id"] == "sku-tea-001"
    assert body["quantity"] == 2
    assert body["status"] == "created"
    assert "id" in body

    fetched = client.get(f"/orders/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


def test_create_order_rejects_invalid_quantity() -> None:
    response = client.post(
        "/orders",
        json={
            "product_id": "sku-tea-001",
            "quantity": 0,
            "customer_email": "guest@gurujix.com",
        },
    )
    assert response.status_code == 422


def test_get_order_not_found() -> None:
    response = client.get("/orders/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
