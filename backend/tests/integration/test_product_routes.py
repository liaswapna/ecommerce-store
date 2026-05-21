from app.models.user import User
from tests.conftest import TestingSession
from app.services.auth import AuthService


auth_service = AuthService()


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


def create_user_token():
    # create a regular non-admin user and return a valid JWT token
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


def create_product(client, token):
    # helper to create a product via the API and return the response data
    response = client.post("/admin/products", json={
        "name": "Nike Air Max",
        "description": "Running shoes",
        "category": "shoes",
        "price": "99.99",
        "stock": 50,
        "is_active": True
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()


class TestAdminGetAllProducts:

    def test_admin_sees_both_active_and_inactive_products(self, client):
        # create two products, delete one — admin should see both
        token = create_admin_token()
        product1 = create_product(client, token)
        create_product(client, token)
        client.delete(f"/admin/products/{product1['id']}",
                      headers={"Authorization": f"Bearer {token}"})
        response = client.get("/admin/products",
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert len(response.json()) == 2
        statuses = [p["is_active"] for p in response.json()]
        assert True in statuses
        assert False in statuses

    def test_no_auth(self, client):
        # no token — should return 403
        response = client.get("/admin/products")
        assert response.status_code == 401

    def test_non_admin_forbidden(self, client):
        # regular user token — should return 403
        token = create_user_token()
        response = client.get("/admin/products",
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


class TestGetAllProducts:

    def test_returns_empty_list_when_no_products(self, client):
        # no products in DB — should return empty list, not an error
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_active_products(self, client):
        # create a product then fetch all — should appear in the list
        token = create_admin_token()
        create_product(client, token)
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_inactive_products_not_shown(self, client):
        # deleted product should not appear in customer list
        token = create_admin_token()
        product = create_product(client, token)
        client.delete(f"/admin/products/{product['id']}",
                      headers={"Authorization": f"Bearer {token}"})
        response = client.get("/products/")
        assert response.json() == []

    def test_pagination(self, client):
        # page_size=1 should return only one product even if two exist
        token = create_admin_token()
        create_product(client, token)
        create_product(client, token)
        response = client.get("/products/?page=1&page_size=1")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestGetProductById:

    def test_returns_product(self, client):
        # create a product then fetch by id — should return correct product
        token = create_admin_token()
        product = create_product(client, token)
        response = client.get(f"/products/{product['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Nike Air Max"

    def test_returns_404_when_not_found(self, client):
        # no product with id 999 — should return 404
        response = client.get("/products/999")
        assert response.status_code == 404


class TestGetByCategory:

    def test_returns_products_in_category(self, client):
        # create a product in shoes — fetching shoes category should return it
        token = create_admin_token()
        create_product(client, token)
        response = client.get("/products/category/shoes")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_returns_empty_for_unknown_category(self, client):
        # no products in electronics — should return empty list, not error
        response = client.get("/products/category/electronics")
        assert response.status_code == 200
        assert response.json() == []


class TestAdminCreateProduct:

    def test_success(self, client):
        # admin creates product — should return created product with id
        token = create_admin_token()
        response = client.post("/admin/products", json={
            "name": "Nike Air Max",
            "description": "Running shoes",
            "category": "shoes",
            "price": "99.99",
            "stock": 50,
            "is_active": True
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nike Air Max"
        assert data["id"] is not None

    def test_no_auth(self, client):
        # no token — HTTPBearer returns 401
        response = client.post("/admin/products", json={
            "name": "Nike Air Max",
            "description": "Running shoes",
            "category": "shoes",
            "price": "99.99",
            "stock": 50
        })
        assert response.status_code == 401

    def test_non_admin_forbidden(self, client):
        # regular user token — require_admin raises 403
        token = create_user_token()
        response = client.post("/admin/products", json={
            "name": "Nike Air Max",
            "description": "Running shoes",
            "category": "shoes",
            "price": "99.99",
            "stock": 50
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_missing_required_field(self, client):
        # missing price — Pydantic returns 422
        token = create_admin_token()
        response = client.post("/admin/products", json={
            "name": "Nike Air Max",
            "category": "shoes",
            "stock": 50
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422


class TestAdminUpdateProduct:

    def test_success(self, client):
        # admin updates product name — should return updated product
        token = create_admin_token()
        product = create_product(client, token)
        response = client.put(f"/admin/products/{product['id']}",
                              json={"name": "Updated Name"},
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_not_found(self, client):
        # product 999 doesn't exist — should return 404
        token = create_admin_token()
        response = client.put("/admin/products/999",
                              json={"name": "Updated Name"},
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_no_auth(self, client):
        # no token — should return 401
        response = client.put("/admin/products/1", json={"name": "Updated Name"})
        assert response.status_code == 401


class TestAdminDeleteProduct:

    def test_success(self, client):
        # admin deletes product — should set is_active=False (soft delete)
        token = create_admin_token()
        product = create_product(client, token)
        response = client.delete(f"/admin/products/{product['id']}",
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_not_found(self, client):
        # product 999 doesn't exist — should return 404
        token = create_admin_token()
        response = client.delete("/admin/products/999",
                                 headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    def test_no_auth(self, client):
        # no token — should return 401
        response = client.delete("/admin/products/1")
        assert response.status_code == 401
