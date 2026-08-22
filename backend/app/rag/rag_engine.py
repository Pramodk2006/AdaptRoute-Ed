"""
RAG Engine — Handles RAG prompt grounding with source citations.
"""
from typing import Dict, List, Tuple
from app.rag.vector_store import VectorStore, global_vector_store
from app.utils.logger import logger


class RAGEngine:
    """RAG engine providing grounding context and reference citations to LLM prompts."""

    def __init__(self, vector_store: VectorStore = global_vector_store):
        self.store = vector_store

    def index_course_material(self, doc_title: str, text: str) -> Dict:
        """Index raw textbook / course text into vector store."""
        ids = self.store.add_document(doc_title, text)
        logger.info(f"Indexed document '{doc_title}' ({len(ids)} chunks created)")
        return {
            "doc_title": doc_title,
            "chunks_created": len(ids),
            "chunk_ids": ids,
        }

    def retrieve_grounding_context(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        """
        Search vector store for relevant chunks and construct grounded context string + citations.

        Returns:
            (context_str, citations_list)
        """
        results = self.store.similarity_search(query, top_k=top_k)
        if not results:
            return "", []

        context_parts = []
        citations = []

        for chunk, score in results:
            citation_label = f"[{chunk.doc_title} (Part {chunk.chunk_index + 1})]"
            context_parts.append(f"Source {citation_label}:\n{chunk.content}")
            citations.append({
                "source": chunk.doc_title,
                "part": chunk.chunk_index + 1,
                "similarity_score": round(score, 4),
                "snippet": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
            })

        context_str = "\n\n".join(context_parts)
        return context_str, citations

    def format_grounded_prompt(self, user_prompt: str, context_str: str) -> str:
        """Build grounded prompt including reference text."""
        if not context_str:
            return user_prompt

        return f"""Reference Course Material (Grounded RAG Context):
{context_str}

Instruction:
Answer the following question using the reference course material above whenever relevant.

Question: {user_prompt}"""


# Global RAG Engine instance
global_rag_engine = RAGEngine()
