from decimal import Decimal
from app.database import database
from app.models.product import Product


products = [
    Product(name="Nike Air Max", description="Comfortable running shoes", image_url="https://example.com/nike-air-max.jpg", category="shoes", price=Decimal("99.99"), stock=50),
    Product(name="Adidas Ultraboost", description="High performance running shoes", image_url="https://example.com/adidas-ultraboost.jpg", category="shoes", price=Decimal("129.99"), stock=30),
    Product(name="New Balance 990", description="Classic everyday sneakers", image_url="https://example.com/nb-990.jpg", category="shoes", price=Decimal("174.99"), stock=20),
    Product(name="Sony WH-1000XM5", description="Noise cancelling wireless headphones", image_url="https://example.com/sony-wh1000xm5.jpg", category="electronics", price=Decimal("349.99"), stock=15),
    Product(name="Apple AirPods Pro", description="Active noise cancellation earbuds", image_url="https://example.com/airpods-pro.jpg", category="electronics", price=Decimal("249.99"), stock=25),
    Product(name="Samsung 4K Monitor", description="27 inch 4K UHD display", image_url="https://example.com/samsung-monitor.jpg", category="electronics", price=Decimal("399.99"), stock=10),
    Product(name="Levi's 501 Jeans", description="Classic straight fit jeans", image_url="https://example.com/levis-501.jpg", category="clothing", price=Decimal("69.99"), stock=40),
    Product(name="North Face Jacket", description="Waterproof hiking jacket", image_url="https://example.com/north-face.jpg", category="clothing", price=Decimal("199.99"), stock=18),
    Product(name="Yoga Mat", description="Non-slip exercise mat", image_url="https://example.com/yoga-mat.jpg", category="sports", price=Decimal("34.99"), stock=60),
    Product(name="Kettlebell 20kg", description="Cast iron kettlebell", image_url="https://example.com/kettlebell.jpg", category="sports", price=Decimal("49.99"), stock=35),
]


def seed():
    db = database.Session()
    try:
        existing = db.query(Product).count()
        if existing > 0:
            print(f"DB already has {existing} products — skipping seed")
            return
        db.add_all(products)
        db.commit()
        print(f"Seeded {len(products)} products")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
