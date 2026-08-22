"""
Vector Store — In-memory vector database with Cosine Similarity search & document chunking.
"""
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class DocumentChunk:
    id: str
    doc_title: str
    content: str
    chunk_index: int
    vector: Dict[str, float]


class VectorStore:
    """In-memory vector database using TF-IDF / Cosine similarity matching."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase words."""
        return re.findall(r"\w+", text.lower())

    def _build_vector(self, text: str) -> Dict[str, float]:
        """Compute term frequency vector for a text string."""
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        total = len(tokens)
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        return {term: count / total for term, count in counts.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two term frequency vectors."""
        common_terms = set(vec1.keys()) & set(vec2.keys())
        if not common_terms:
            return 0.0

        dot_product = sum(vec1[t] * vec2[t] for t in common_terms)
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def add_document(self, doc_title: str, text: str, chunk_size: int = 200) -> List[str]:
        """
        Chunk text and add to vector store index.
        Returns list of generated chunk IDs.
        """
        words = text.split()
        added_ids = []

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunk_id = f"{doc_title}_{len(self.chunks)}"
            vec = self._build_vector(chunk_text)

            chunk_obj = DocumentChunk(
                id=chunk_id,
                doc_title=doc_title,
                content=chunk_text,
                chunk_index=i // chunk_size,
                vector=vec,
            )
            self.chunks.append(chunk_obj)
            added_ids.append(chunk_id)

        return added_ids

    def similarity_search(self, query: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """Find top_k document chunks most similar to query string."""
        query_vec = self._build_vector(query)
        if not query_vec or not self.chunks:
            return []

        scored = []
        for chunk in self.chunks:
            score = self._cosine_similarity(query_vec, chunk.vector)
            scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [(chunk, score) for chunk, score in scored[:top_k] if score > 0.0]


# Global vector store instance
global_vector_store = VectorStore()
