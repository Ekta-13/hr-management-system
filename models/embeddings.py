"""
models/embeddings.py — Sentence Transformer model loader and cosine similarity scoring
"""
import numpy as np
from functools import lru_cache


@lru_cache(maxsize=1)
def load_model():
    """Load model once and cache it for the session."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model
    except Exception:
        return None


def get_embedding(text: str):
    model = load_model()
    if model is None:
        return None
    return model.encode(text, convert_to_numpy=True)


def cosine_similarity(vec_a, vec_b) -> float:
    if vec_a is None or vec_b is None:
        return 0.0
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    return float(dot / norm) if norm > 0 else 0.0


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Compute semantic similarity between resume and JD using sentence embeddings.
    Returns a score between 0 and 100.
    """
    emb_resume = get_embedding(resume_text[:2000])
    emb_jd = get_embedding(job_description[:2000])
    similarity = cosine_similarity(emb_resume, emb_jd)
    # Convert cosine similarity (-1 to 1) to percentage (0 to 100)
    score = (similarity + 1) / 2 * 100
    return round(score, 1)
