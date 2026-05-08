class TestRegister:
    def test_success(self, client):
        response = client.post("/auth/register", json={
            "name": "Sarah",
            "email": "sarah@example.com",
            "password": "secret123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "sarah@example.com"
        assert data["name"] == "Sarah"
        assert "password" not in data

    def test_duplicate_email(self, client):
        client.post("/auth/register", json={
            "name": "Sarah",
            "email": "sarah@example.com",
            "password": "secret123"
        })
        response = client.post("/auth/register", json={
            "name": "Sarah",
            "email": "sarah@example.com",
            "password": "secret123"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_invalid_email(self, client):
        response = client.post("/auth/register", json={
            "name": "Sarah",
            "email": "not-an-email",
            "password": "secret123"
        })
        assert response.status_code == 422

    def test_missing_fields(self, client):
        response = client.post("/auth/register", json={
            "name": "Sarah"
        })
        assert response.status_code == 422


class TestLogin:
    def test_success(self, client):
        client.post("/auth/register", json={
            "name": "Sarah",
            "email": "sarah@example.com",
            "password": "secret123"
        })
        response = client.post("/auth/login", json={
            "email": "sarah@example.com",
            "password": "secret123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_wrong_password(self, client):
        client.post("/auth/register", json={
            "name": "Sarah",
            "email": "sarah@example.com",
            "password": "secret123"
        })
        response = client.post("/auth/login", json={
            "email": "sarah@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_wrong_email(self, client):
        response = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "secret123"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"
