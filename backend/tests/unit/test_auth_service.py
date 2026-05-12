import pytest
from app.services.auth import AuthService

service = AuthService()


class TestHashPassword:

    def test_returns_string(self):
        result = service.hash_password("secret123")
        assert isinstance(result, str)

    def test_hash_differs_from_plain(self):
        result = service.hash_password("secret123")
        assert result != "secret123"

    def test_same_password_different_hashes(self):
        hash1 = service.hash_password("secret123")
        hash2 = service.hash_password("secret123")
        assert hash1 != hash2


class TestVerifyPassword:

    def test_correct_password_returns_true(self):
        hashed = service.hash_password("secret123")
        assert service.verify_password("secret123", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = service.hash_password("secret123")
        assert service.verify_password("wrongpassword", hashed) is False


class TestCreateToken:

    def test_returns_string(self):
        token = service.create_token(1)
        assert isinstance(token, str)

    def test_token_contains_user_id(self):
        import jwt
        from app.services.auth import SECRET_KEY, ALGORITHM
        token = service.create_token(1)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"
