# Turns text into "score cards" (embeddings): lists of numbers that capture meaning.
# Products and search words get cards; similar meanings get similar cards.

from functools import lru_cache
from typing import Protocol

from google import genai
from google.genai import types

from app.config import settings

# The Gemini model that makes the cards. Every card must come from the SAME model,
# otherwise cards can't be compared (two different "schools"). Changing it means re-embedding all products.
EMBEDDING_MODEL = "gemini-embedding-001"

# How many spots (numbers) on each card. Must match Vector(768) on Product.embedding.
EMBEDDING_DIMENSIONS = 768


# The "job description" (interface): anything with an embed() that turns a list of texts
# into a list of cards counts as an Embedder. The rest of the app only talks to this,
# so tests can swap in a fake worker without changing app code.
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


# The real worker: asks Google's Gemini to make the cards (needs internet + API key).
class GeminiEmbedder:
    def __init__(self, api_key: str):
        # connect to Gemini once, when the worker is created
        self.client = genai.Client(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        # one call can embed several texts at once; we get one card back per text, in the same order
        result = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                # tells Gemini we will COMPARE meanings with these cards
                task_type="SEMANTIC_SIMILARITY",
                # ask for 768-spot cards instead of the full 3,072 (smaller, faster, nearly the same quality)
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
        # Gemini returns an object; keep just the list of numbers for each text
        return [e.values for e in result.embeddings]


# "Hand me a worker" (like get_db for the database). Routes will use Depends(get_embedder);
# tests replace it with a fake via app.dependency_overrides.
# @lru_cache: create the worker once and reuse it, instead of reconnecting on every request.
@lru_cache
def get_embedder() -> Embedder | None:
    # no key set (tests, CI, or a missing Render setting) -> no worker -> callers fall back to keyword search
    if not settings.gemini_api_key:
        return None
    return GeminiEmbedder(settings.gemini_api_key)
