# Pretend embedders for tests: no internet, no API key, free, and the same answer every run.
# Both have embed(texts), so they fit the Embedder type and can replace GeminiEmbedder in tests.

from app.services.embedder import EMBEDDING_DIMENSIONS

# Our hand-made "spots" (like toy_example.py): spot 1 = sporty, spot 2 = warm, spot 3 = music.
# A word from a list appearing in the text turns that spot on.
THEMES = {
    "sporty": ["run", "jogging", "shoes", "marathon", "yoga", "gym"],
    "warm": ["warm", "jacket", "winter", "snow", "cozy"],
    "music": ["music", "headphones", "tunes", "audio"],
}


# Pretend worker #1: makes simple score cards from keywords.
class FakeEmbedder:
    def __init__(self):
        # remembers every list of texts it was asked to embed, so tests can check it was called
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [self._card(text) for text in texts]

    def _card(self, text: str) -> list[float]:
        lowered = text.lower()
        # 1.0 if any of the theme's words appear in the text, else 0.0  ->  e.g. [1.0, 0.0, 0.0]
        card = [1.0 if any(word in lowered for word in words) else 0.0 for words in THEMES.values()]
        # a small extra spot so a card is never all zeros (all-zero cards can't be compared)
        card.append(0.1)
        # fill the rest with zeros so every card has exactly 768 spots, like the real ones
        return card + [0.0] * (EMBEDDING_DIMENSIONS - len(card))


# Pretend worker #2: always fails, to test that the store falls back to keyword search.
class FailingEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Embedding service is down")
