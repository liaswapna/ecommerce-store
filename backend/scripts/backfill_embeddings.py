from app.database import database
from app.embedder import get_embedder
from app.models.product import Product
from app.services.product import ProductService

BATCH_SIZE = 50


def backfill():
    embedder = get_embedder()
    if embedder is None:
        print("GEMINI_API_KEY is not set — nothing to do")
        return
    db = database.Session()
    try:
        products = db.query(Product).filter(Product.embedding.is_(None)).all()
        if not products:
            print("All products already have embeddings")
            return
        for start in range(0, len(products), BATCH_SIZE):
            batch = products[start:start + BATCH_SIZE]
            texts = [ProductService.product_text(p) for p in batch]
            embeddings = embedder.embed(texts)
            for product, embedding in zip(batch, embeddings):
                product.embedding = embedding
            db.commit()
            print(f"Embedded {len(batch)} products")
        print(f"Done: {len(products)} products embedded")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
