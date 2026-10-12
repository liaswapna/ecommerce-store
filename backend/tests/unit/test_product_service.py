from unittest.mock import MagicMock
from decimal import Decimal
import pytest
from app.services.product import ProductService
from app.models.product import Product
from app.schemas.product import UpdateProductRequest
from app.exceptions import NotFoundError, DatabaseError
from tests.fakes import FakeEmbedder


service = ProductService()


def make_product(**kwargs):
    # helper to create a Product object with sensible defaults — override any field via kwargs
    defaults = dict(id=1, name="Nike Air Max", description="Running shoes",
                    image_url=None, category="shoes", price=Decimal("99.99"),
                    stock=50, is_active=True)
    defaults.update(kwargs)
    product = Product(**defaults)
    return product


class TestGetById:

    def test_returns_product_when_found(self):
        # repository returns a product — service should return it unchanged
        db = MagicMock()
        product = make_product()
        service.repository.get_by_id = MagicMock(return_value=product)
        result = service.get_by_id(db, 1)
        assert result.id == 1
        assert result.name == "Nike Air Max"

    def test_raises_not_found_when_missing(self):
        # repository returns None — service should raise NotFoundError
        db = MagicMock()
        service.repository.get_by_id = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.get_by_id(db, 999)


class TestCreate:

    def test_returns_created_product(self):
        # repository creates and returns product — service should pass it back
        db = MagicMock()
        product = make_product()
        service.repository.create = MagicMock(return_value=product)
        data = MagicMock()
        result = service.create(db, data)
        assert result.name == "Nike Air Max"

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        service.repository.create = MagicMock(side_effect=Exception("DB error"))
        data = MagicMock()
        with pytest.raises(DatabaseError):
            service.create(db, data)


class TestUpdate:

    def test_returns_updated_product(self):
        # repository returns updated product — service should return it
        db = MagicMock()
        product = make_product(name="Updated Name")
        service.repository.update = MagicMock(return_value=product)
        data = MagicMock()
        result = service.update(db, data, 1)
        assert result.name == "Updated Name"

    def test_raises_not_found_when_missing(self):
        # repository returns None — product with that id doesn't exist
        db = MagicMock()
        service.repository.update = MagicMock(return_value=None)
        data = MagicMock()
        with pytest.raises(NotFoundError):
            service.update(db, data, 999)

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        service.repository.update = MagicMock(side_effect=Exception("DB error"))
        data = MagicMock()
        with pytest.raises(DatabaseError):
            service.update(db, data, 1)


class TestDelete:

    def test_returns_deleted_product(self):
        # soft delete — repository sets is_active=False and returns the product
        db = MagicMock()
        product = make_product(is_active=False)
        service.repository.delete = MagicMock(return_value=product)
        result = service.delete(db, 1)
        assert result.is_active is False

    def test_raises_not_found_when_missing(self):
        # repository returns None — product with that id doesn't exist
        db = MagicMock()
        service.repository.delete = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.delete(db, 999)

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        service.repository.delete = MagicMock(side_effect=Exception("DB error"))
        with pytest.raises(DatabaseError):
            service.delete(db, 1)


class TestEmbeddingOnUpdate:

    def test_price_only_change_does_not_re_embed(self):
        # only the price changed and the product already has a card -> no new card needed
        db = MagicMock()
        product = make_product(embedding=[0.1] * 768)
        service.repository.update = MagicMock(return_value=product)
        service.repository.update_embedding = MagicMock()
        embedder = FakeEmbedder()
        service.update(db, UpdateProductRequest(price=Decimal("79.99")), 1, embedder)
        assert embedder.calls == []
        service.repository.update_embedding.assert_not_called()

    def test_description_change_re_embeds(self):
        # the description changed -> the meaning changed -> make a new card
        db = MagicMock()
        product = make_product(embedding=[0.1] * 768)
        service.repository.update = MagicMock(return_value=product)
        service.repository.update_embedding = MagicMock()
        embedder = FakeEmbedder()
        service.update(db, UpdateProductRequest(description="Trail running shoes"), 1, embedder)
        assert len(embedder.calls) == 1
        service.repository.update_embedding.assert_called_once()
