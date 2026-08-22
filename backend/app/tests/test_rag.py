"""
RAG Engine & Vector Store unit tests.
"""
from app.rag.vector_store import VectorStore
from app.rag.rag_engine import RAGEngine


def test_vector_store_indexing_and_similarity_search():
    """Vector store chunks document and retrieves relevant text via cosine similarity."""
    store = VectorStore()
    doc_text = (
        "Binary Search Trees (BST) are node-based binary tree data structures "
        "where the left sub-tree contains nodes with keys less than the parent, "
        "and the right sub-tree contains nodes with keys greater than the parent. "
        "Time complexity for search in a balanced BST is O(log n)."
    )

    ids = store.add_document("BST_Chapter_1", doc_text, chunk_size=20)
    assert len(ids) > 0

    results = store.similarity_search("time complexity of binary search tree search", top_k=2)
    assert len(results) > 0
    chunk, score = results[0]
    assert "BST_Chapter_1" in chunk.doc_title
    assert score > 0.0


def test_rag_engine_context_retrieval_and_formatting():
    """RAGEngine indexes material, constructs grounded context, and formats prompt."""
    store = VectorStore()
    engine = RAGEngine(vector_store=store)

    index_res = engine.index_course_material(
        "Python_Data_Structures",
        "Python dictionaries use hash tables for O(1) average time complexity key-value lookups."
    )
    assert index_res["chunks_created"] > 0

    context_str, citations = engine.retrieve_grounding_context("How do Python dictionaries work?", top_k=1)
    assert len(citations) == 1
    assert citations[0]["source"] == "Python_Data_Structures"

    grounded_prompt = engine.format_grounded_prompt("Explain Python dict lookups", context_str)
    assert "Reference Course Material" in grounded_prompt
    assert "Python dictionaries use hash tables" in grounded_prompt


def test_rag_api_endpoints(client, auth_headers):
    """Test POST /api/v1/rag/index and POST /api/v1/rag/search endpoints."""
    # 1. Index document
    index_payload = {
        "doc_title": "Machine_Learning_Notes",
        "content": "Supervised learning uses labeled dataset to train classification and regression algorithms.",
    }
    res_index = client.post("/api/v1/rag/index", json=index_payload, headers=auth_headers)
    assert res_index.status_code == 201
    assert res_index.json()["doc_title"] == "Machine_Learning_Notes"

    # 2. Search document
    search_payload = {
        "query": "What is supervised learning?",
        "top_k": 2,
    }
    res_search = client.post("/api/v1/rag/search", json=search_payload, headers=auth_headers)
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["query"] == "What is supervised learning?"
    assert len(search_data["citations"]) > 0
