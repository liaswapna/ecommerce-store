from app.database import database
from app.embedder import get_embedder
from app.repositories.product import ProductRepository

TOP_K = 3

CASES = [
    ("something for walking", ["Trail Walking Shoes"]),
    ("reading books on vacation", ["E-Reader"]),
    ("video calls from home", ["HD Webcam"]),
    ("listen to music on the train", ["Sony WH-1000XM5", "Apple AirPods Pro"]),
    ("stay dry in the rain", ["Lightweight Rain Jacket", "Rain Boots"]),
    ("freezing winter day outfit", ["Down Puffer Coat"]),
    ("charge my phone while traveling", ["Power Bank 20000mAh"]),
    ("sore muscles after the gym", ["Foam Roller"]),
    ("camping overnight in the cold", ["Cold-Weather Sleeping Bag"]),
    ("shoes for a wedding", ["Formal Oxford Shoes"]),
    ("protect my head on a bike", ["Bike Helmet"]),
    ("beach holiday swimwear", ["Swim Shorts"]),
    ("track my steps and sleep", ["Smartwatch Fitness Tracker"]),
    ("sandals", ["Leather Sandals"]),
    ("webcam", ["HD Webcam"]),
]


def evaluate():
    embedder = get_embedder()
    if embedder is None:
        print("GEMINI_API_KEY is not set — nothing to do")
        return
    repository = ProductRepository()
    db = database.Session()
    try:
        query_embeddings = embedder.embed([query for query, _ in CASES])
        keyword_hits = 0
        semantic_hits = 0
        for (query, expected), query_embedding in zip(CASES, query_embeddings):
            keyword_names = [p.name for p in repository.search_by_keyword(db, query, TOP_K)]
            semantic_names = [p.name for p in repository.search_by_embedding(db, query_embedding, TOP_K)]
            keyword_ok = any(name in keyword_names for name in expected)
            semantic_ok = any(name in semantic_names for name in expected)
            keyword_hits += keyword_ok
            semantic_hits += semantic_ok
            print(f"keyword {'✅' if keyword_ok else '❌'}   semantic {'✅' if semantic_ok else '❌'}   {query}")
        total = len(CASES)
        print(f"\nHit rate @{TOP_K}:  keyword {keyword_hits}/{total}   semantic {semantic_hits}/{total}")
    finally:
        db.close()


if __name__ == "__main__":
    evaluate()
