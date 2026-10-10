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
    Product(name='Trail Walking Shoes', description='Lightweight walking shoes with cushioned soles for daily walks, errands and light trails.', image_url=None, category="shoes", price=Decimal("89.99"), stock=40),
    Product(name='Waterproof Hiking Boots', description='Ankle-high waterproof boots with grippy soles for muddy mountain hikes.', image_url=None, category="shoes", price=Decimal("149.99"), stock=25),
    Product(name='Leather Sandals', description='Breathable leather sandals for hot summer days at the beach or around town.', image_url=None, category="shoes", price=Decimal("49.99"), stock=35),
    Product(name="Kids' Light-Up Sneakers", description='Colorful sneakers for children with lights that flash with every step.', image_url=None, category="shoes", price=Decimal("39.99"), stock=50),
    Product(name='Formal Oxford Shoes', description='Polished leather dress shoes for weddings, interviews and the office.', image_url=None, category="shoes", price=Decimal("129.99"), stock=20),
    Product(name='Wool House Slippers', description='Soft wool-lined slippers that keep your feet warm at home on cold evenings.', image_url=None, category="shoes", price=Decimal("34.99"), stock=45),
    Product(name='Trail Running Shoes', description='Rugged running shoes with deep tread for off-road runs on dirt and rocks.', image_url=None, category="shoes", price=Decimal("119.99"), stock=30),
    Product(name='Basketball High-Tops', description='High-top court shoes with ankle support for jumping and quick cuts.', image_url=None, category="shoes", price=Decimal("109.99"), stock=25),
    Product(name='Insulated Snow Boots', description='Fleece-lined winter boots that stay dry and warm in deep snow.', image_url=None, category="shoes", price=Decimal("139.99"), stock=20),
    Product(name='Cycling Shoes', description='Stiff-soled shoes that clip into bike pedals for efficient road cycling.', image_url=None, category="shoes", price=Decimal("99.99"), stock=15),
    Product(name='Canvas Slip-Ons', description='Easy slip-on canvas shoes for casual weekends and quick trips out.', image_url=None, category="shoes", price=Decimal("44.99"), stock=40),
    Product(name='Rain Boots', description='Tall rubber boots that keep feet dry when walking through puddles and rain.', image_url=None, category="shoes", price=Decimal("54.99"), stock=30),
    Product(name='Barefoot Minimalist Shoes', description='Thin flexible shoes that feel like walking barefoot, for natural movement.', image_url=None, category="shoes", price=Decimal("94.99"), stock=20),
    Product(name='Portable Bluetooth Speaker', description='Waterproof pocket speaker for playing music outdoors, at the pool or on a picnic.', image_url=None, category="electronics", price=Decimal("59.99"), stock=40),
    Product(name='E-Reader', description='Glare-free e-ink reader that holds thousands of books for reading on trips.', image_url=None, category="electronics", price=Decimal("129.99"), stock=25),
    Product(name='Smartwatch Fitness Tracker', description='Watch that tracks steps, heart rate and sleep, with phone notifications.', image_url=None, category="electronics", price=Decimal("199.99"), stock=20),
    Product(name='Action Camera', description='Tough mini camera for filming biking, surfing and adventure videos in 4K.', image_url=None, category="electronics", price=Decimal("249.99"), stock=15),
    Product(name='Power Bank 20000mAh', description='High-capacity battery pack to charge your phone several times while travelling.', image_url=None, category="electronics", price=Decimal("39.99"), stock=60),
    Product(name='Mechanical Keyboard', description='Clicky mechanical keyboard with backlit keys for typing and gaming.', image_url=None, category="electronics", price=Decimal("89.99"), stock=30),
    Product(name='HD Webcam', description='Full HD webcam with built-in microphone for video calls and online classes.', image_url=None, category="electronics", price=Decimal("69.99"), stock=35),
    Product(name='Ergonomic Vertical Mouse', description='Vertical mouse that reduces wrist strain during long days at the computer.', image_url=None, category="electronics", price=Decimal("49.99"), stock=30),
    Product(name='Smart Home Speaker', description='Voice-controlled speaker that answers questions, plays music and controls smart lights.', image_url=None, category="electronics", price=Decimal("99.99"), stock=25),
    Product(name='Digital Drawing Tablet', description='Pen tablet for sketching, digital art and photo editing on your computer.', image_url=None, category="electronics", price=Decimal("79.99"), stock=20),
    Product(name="Kids' Tablet", description='Durable tablet with parental controls and educational games for children.', image_url=None, category="electronics", price=Decimal("119.99"), stock=25),
    Product(name='Wireless Phone Charger', description='Charging pad that powers up your phone when you set it down, no cables needed.', image_url=None, category="electronics", price=Decimal("29.99"), stock=50),
    Product(name='Merino Wool Sweater', description='Warm, itch-free wool sweater for chilly autumn and winter days.', image_url=None, category="clothing", price=Decimal("89.99"), stock=30),
    Product(name='Lightweight Rain Jacket', description='Packable waterproof shell that keeps you dry during sudden showers.', image_url=None, category="clothing", price=Decimal("79.99"), stock=35),
    Product(name='Cotton T-Shirt Pack', description='Set of three soft everyday crew-neck t-shirts in basic colors.', image_url=None, category="clothing", price=Decimal("29.99"), stock=60),
    Product(name='Down Puffer Coat', description='Thick insulated winter coat for freezing temperatures and snowy days.', image_url=None, category="clothing", price=Decimal("179.99"), stock=20),
    Product(name='Swim Shorts', description='Quick-dry swim trunks for the beach, pool and summer holidays.', image_url=None, category="clothing", price=Decimal("34.99"), stock=40),
    Product(name='Linen Summer Dress', description='Light, breathable linen dress for hot weather and vacations.', image_url=None, category="clothing", price=Decimal("69.99"), stock=25),
    Product(name='Thermal Base Layer Set', description='Warm top and leggings worn under clothes for skiing and cold outdoor work.', image_url=None, category="clothing", price=Decimal("59.99"), stock=30),
    Product(name='Business Blazer', description='Tailored blazer for meetings, interviews and formal events.', image_url=None, category="clothing", price=Decimal("159.99"), stock=15),
    Product(name='Fleece Hoodie', description='Cozy zip-up hoodie for lounging at home or cool evenings outside.', image_url=None, category="clothing", price=Decimal("49.99"), stock=45),
    Product(name='Wool Beanie and Gloves Set', description='Knitted hat and gloves that keep your head and hands warm in winter.', image_url=None, category="clothing", price=Decimal("24.99"), stock=50),
    Product(name='Cotton Pajama Set', description="Soft cotton pajamas for a comfortable night's sleep.", image_url=None, category="clothing", price=Decimal("39.99"), stock=35),
    Product(name='Wide-Brim Sun Hat', description='Wide-brim hat that shades your face and neck on sunny hikes and beach days.', image_url=None, category="clothing", price=Decimal("27.99"), stock=40),
    Product(name='Running Shorts', description='Lightweight shorts with a zip pocket for jogging and gym workouts.', image_url=None, category="clothing", price=Decimal("29.99"), stock=45),
    Product(name='Adjustable Dumbbells', description='Pair of dumbbells with adjustable weights for strength training at home.', image_url=None, category="sports", price=Decimal("149.99"), stock=20),
    Product(name='Bike Helmet', description='Lightweight ventilated helmet that protects your head while cycling.', image_url=None, category="sports", price=Decimal("69.99"), stock=30),
    Product(name='Tennis Racket', description='Graphite racket for beginner and intermediate tennis players.', image_url=None, category="sports", price=Decimal("89.99"), stock=20),
    Product(name='Two-Person Camping Tent', description='Easy-setup waterproof tent for weekend camping trips for two.', image_url=None, category="sports", price=Decimal("129.99"), stock=15),
    Product(name='Hiking Backpack 40L', description='Comfortable backpack with rain cover for day hikes and overnight trips.', image_url=None, category="sports", price=Decimal("99.99"), stock=25),
    Product(name='Jump Rope', description='Speed jump rope for cardio workouts, boxing training and warm-ups.', image_url=None, category="sports", price=Decimal("14.99"), stock=60),
    Product(name='Resistance Bands Set', description='Five stretchy bands of different strengths for home workouts and physical therapy.', image_url=None, category="sports", price=Decimal("24.99"), stock=50),
    Product(name='Soccer Ball', description='Durable size-5 ball for matches, practice and playing in the park.', image_url=None, category="sports", price=Decimal("29.99"), stock=40),
    Product(name='Swimming Goggles', description='Anti-fog goggles for clear vision when swimming laps in the pool.', image_url=None, category="sports", price=Decimal("19.99"), stock=50),
    Product(name='Foam Roller', description='Firm foam roller for stretching and easing sore muscles after exercise.', image_url=None, category="sports", price=Decimal("24.99"), stock=40),
    Product(name='Cold-Weather Sleeping Bag', description='Warm mummy sleeping bag for camping in cold weather.', image_url=None, category="sports", price=Decimal("79.99"), stock=20),
    Product(name='Basketball', description='Indoor/outdoor basketball with a grippy surface for pickup games.', image_url=None, category="sports", price=Decimal("34.99"), stock=35),
]


def seed():
    db = database.Session()
    try:
        existing_names = {name for (name,) in db.query(Product.name).all()}
        new_products = [p for p in products if p.name not in existing_names]
        if not new_products:
            print("All seed products already exist — nothing to add")
            return
        db.add_all(new_products)
        db.commit()
        print(f"Added {len(new_products)} products ({len(existing_names)} already existed)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
