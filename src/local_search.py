from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = f"{current}\n\n{p}".strip()
        else:
            if current:
                chunks.append(current)
            current = p

    if current:
        chunks.append(current)

    return chunks or [text[:max_chars]]


@lru_cache(maxsize=1)
def _build_index(base_dir: str = "knowledge_base") -> Dict[str, Any]:
    base_path = Path(base_dir)
    docs: List[Dict[str, Any]] = []

    for path in base_path.rglob("*"):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, chunk in enumerate(_chunk_text(text)):
            docs.append(
                {
                    "path": str(path),
                    "chunk_id": idx,
                    "text": chunk,
                }
            )

    if not docs:
        return {"docs": [], "vectorizer": None, "matrix": None}

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([d["text"] for d in docs])

    return {"docs": docs, "vectorizer": vectorizer, "matrix": matrix}


def search_local_docs(query: str, top_k: int = 3, base_dir: str = "knowledge_base") -> Dict[str, Any]:
    index = _build_index(base_dir)
    docs = index["docs"]
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]

    if not docs or vectorizer is None or matrix is None:
        return {"query": query, "hits": []}

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix).flatten()
    ranked = scores.argsort()[::-1][:top_k]

    hits = []
    for idx in ranked:
        score = float(scores[idx])
        if score <= 0:
            continue

        doc = docs[idx]
        hits.append(
            {
                "path": doc["path"],
                "chunk_id": doc["chunk_id"],
                "score": round(score, 4),
                "snippet": doc["text"][:500].replace("\n", " "),
            }
        )

    return {"query": query, "hits": hits}