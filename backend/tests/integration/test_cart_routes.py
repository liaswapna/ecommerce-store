from app.models.user import User
from tests.conftest import TestingSession
from app.services.auth import AuthService


auth_service = AuthService()


def create_user_token():
    # create a regular user directly in the test DB and return a valid JWT token
    db = TestingSession()
    try:
        user = User(name="User", email="user@example.com",
                    hashed_password=auth_service.hash_password("user123"), is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        return auth_service.create_token(user.id)
    finally:
        db.close()


def create_admin_token():
    # create an admin user directly in the test DB and return a valid JWT token
    db = TestingSession()
    try:
        user = User(name="Admin", email="admin@example.com",
                    hashed_password=auth_service.hash_password("admin123"), is_admin=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return auth_service.create_token(user.id)
    finally:
        db.close()


def create_product(client, token, stock=50):
    # helper to create a product via the API and return the response data
    response = client.post("/admin/products", json={
        "name": "Nike Air Max",
        "description": "Running shoes",
        "category": "shoes",
        "price": "99.99",
        "stock": stock,
        "is_active": True
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()


class TestGetCart:

    def test_returns_empty_list_when_cart_is_empty(self, client):
        # no items in cart — should return empty list
        token = create_user_token()
        response = client.get("/cart/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_cart_items_with_product_details(self, client):
        # add an item then fetch cart — should return item with name and price
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                    headers={"Authorization": f"Bearer {user_token}"})
        response = client.get("/cart/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["quantity"] == 2
        assert data[0]["name"] == "Nike Air Max"
        assert data[0]["price"] == "99.99"

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.get("/cart/")
        assert response.status_code == 401


class TestAddToCart:

    def test_success(self, client):
        # product exists with enough stock — should add to cart and return cart item
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        response = client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                               headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product["id"]
        assert data["quantity"] == 2

    def test_product_not_found_returns_404(self, client):
        # product 999 doesn't exist — should return 404
        token = create_user_token()
        response = client.post("/cart/", json={"product_id": 999, "quantity": 1},
                               headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_out_of_stock_returns_400(self, client):
        # product stock is 1, requesting 5 — should return 400
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=1)
        response = client.post("/cart/", json={"product_id": product["id"], "quantity": 5},
                               headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 400

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.post("/cart/", json={"product_id": 1, "quantity": 1})
        assert response.status_code == 401

    def test_invalid_quantity_returns_422(self, client):
        # quantity 0 violates ge=1 — Pydantic returns 422
        token = create_user_token()
        response = client.post("/cart/", json={"product_id": 1, "quantity": 0},
                               headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422


class TestUpdateCart:

    def test_success(self, client):
        # item in cart — update quantity and return updated item
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                    headers={"Authorization": f"Bearer {user_token}"})
        response = client.patch("/cart/", json={"product_id": product["id"], "quantity": 5},
                                headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()["quantity"] == 5

    def test_product_not_found_returns_404(self, client):
        # product 999 doesn't exist — should return 404
        token = create_user_token()
        response = client.patch("/cart/", json={"product_id": 999, "quantity": 1},
                                headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_cart_item_not_found_returns_404(self, client):
        # product exists but not in cart — should return 404
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        response = client.patch("/cart/", json={"product_id": product["id"], "quantity": 2},
                                headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 404

    def test_out_of_stock_returns_400(self, client):
        # product stock is 2, requesting 10 — should return 400
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=2)
        client.post("/cart/", json={"product_id": product["id"], "quantity": 1},
                    headers={"Authorization": f"Bearer {user_token}"})
        response = client.patch("/cart/", json={"product_id": product["id"], "quantity": 10},
                                headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 400

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.patch("/cart/", json={"product_id": 1, "quantity": 2})
        assert response.status_code == 401


class TestDeleteFromCart:

    def test_success(self, client):
        # item in cart — delete it and return the deleted item with is_active check skipped
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                    headers={"Authorization": f"Bearer {user_token}"})
        response = client.delete(f"/cart/{product['id']}",
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()["product_id"] == product["id"]

    def test_cart_item_not_found_returns_404(self, client):
        # product exists but not in cart — should return 404
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        response = client.delete(f"/cart/{product['id']}",
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 404

    def test_product_not_found_returns_404(self, client):
        # product 999 doesn't exist — should return 404
        token = create_user_token()
        response = client.delete("/cart/999",
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.delete("/cart/1")
        assert response.status_code == 401


class TestClearCart:

    def test_success(self, client):
        # items in cart — clear all and verify cart is empty
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token)
        client.post("/cart/", json={"product_id": product["id"], "quantity": 2},
                    headers={"Authorization": f"Bearer {user_token}"})
        response = client.delete("/cart/clear", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        cart = client.get("/cart/", headers={"Authorization": f"Bearer {user_token}"})
        assert cart.json() == []

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.delete("/cart/clear")
        assert response.status_code == 401
