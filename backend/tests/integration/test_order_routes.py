from decimal import Decimal
from app.models.user import User
from tests.conftest import TestingSession
from app.services.auth import AuthService
from app.models.product import Product as ProductModel


auth_service = AuthService()


def create_user_token():
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
    response = client.post("/admin/products", json={
        "name": "Nike Air Max",
        "description": "Running shoes",
        "category": "shoes",
        "price": "99.99",
        "stock": stock,
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()


def add_to_cart(client, token, product_id, quantity=2):
    return client.post("/cart/", json={"product_id": product_id, "quantity": quantity},
                       headers={"Authorization": f"Bearer {token}"})


class TestPlaceOrder:

    def test_success(self, client):
        # user has items in cart — order is created, stock decremented, cart cleared
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=2)

        response = client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert Decimal(data["total_price"]) == Decimal("99.99") * 2
        assert len(data["items"]) == 1
        assert data["items"][0]["name_at_purchase"] == "Nike Air Max"
        assert data["items"][0]["quantity"] == 2

    def test_cart_cleared_after_order(self, client):
        # after placing order, cart should be empty
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=2)

        client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})

        cart = client.get(
            "/cart/", headers={"Authorization": f"Bearer {user_token}"})
        assert cart.json() == []

    def test_stock_decremented_after_order(self, client):
        # after placing order, product stock should be reduced
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=3)

        client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})

        updated = client.get(f"/products/{product['id']}")
        assert updated.json()["stock"] == 7

    def test_empty_cart_returns_404(self, client):
        # no items in cart — should return 404
        user_token = create_user_token()
        response = client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 404

    def test_out_of_stock_returns_400(self, client):
        # cart has quantity 5 but stock is only 1 — place order should return 400
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=5)

        # drain stock so it's below cart quantity
        db = TestingSession()

        db.query(ProductModel).filter(ProductModel.id ==
                                      product["id"]).update({"stock": 1})
        db.commit()
        db.close()

        response = client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 400

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.post("/orders/")
        assert response.status_code == 401


class TestGetOrders:

    def test_returns_empty_list_when_no_orders(self, client):
        # user has no orders — should return empty list
        user_token = create_user_token()
        response = client.get(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_orders_after_placing_one(self, client):
        # user places an order — GET /orders should return it
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=2)
        client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})

        response = client.get(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
        assert "items" not in data[0]

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.get("/orders/")
        assert response.status_code == 401


class TestGetOrderById:

    def test_returns_order_with_items(self, client):
        # place an order then fetch it by id — should return full detail with items
        admin_token = create_admin_token()
        user_token = create_user_token()
        product = create_product(client, admin_token, stock=10)
        add_to_cart(client, user_token, product["id"], quantity=2)
        order = client.post(
            "/orders/", headers={"Authorization": f"Bearer {user_token}"}).json()

        response = client.get(
            f"/orders/{order['id']}", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order["id"]
        assert len(data["items"]) == 1
        assert data["items"][0]["name_at_purchase"] == "Nike Air Max"

    def test_order_not_found_returns_404(self, client):
        # order 999 doesn't exist — should return 404
        user_token = create_user_token()
        response = client.get(
            "/orders/999", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 404

    def test_no_token_returns_401(self, client):
        # no token — should return 401
        response = client.get("/orders/1")
        assert response.status_code == 401
