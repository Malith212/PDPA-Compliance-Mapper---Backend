"""
Thin wrapper around sentence-transformers.

Loading the model is slow (a few seconds, plus a one-time download), so we
load it ONCE at process startup and reuse it for every request, rather than
reloading it per-request.
"""

from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good general-purpose model


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed(texts: list[str]) -> np.ndarray:
    """Embed a list of strings into an array of vectors."""
    model = get_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity between two already-normalised vectors."""
    return float(util.cos_sim(vec_a, vec_b).item())
