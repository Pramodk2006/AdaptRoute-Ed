"""
RAG Router — /api/v1/rag endpoints for document indexing and similarity search.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models.user import User
from app.rag import global_rag_engine
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG & Vector Grounding"])


class IndexDocumentRequest(BaseModel):
    doc_title: str
    content: str


class IndexDocumentResponse(BaseModel):
    doc_title: str
    chunks_created: int
    chunk_ids: List[str]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class CitationChunk(BaseModel):
    source: str
    part: int
    similarity_score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    grounding_context: str
    citations: List[CitationChunk]


@router.post("/index", response_model=IndexDocumentResponse, status_code=status.HTTP_201_CREATED,
             summary="Index educational document into vector store")
def index_document(
    body: IndexDocumentRequest,
    current_user: User = Depends(get_current_user),
):
    """Chunk and index document text into vector similarity store."""
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")
    result = global_rag_engine.index_course_material(body.doc_title, body.content)
    return IndexDocumentResponse(**result)


@router.post("/search", response_model=SearchResponse,
             summary="Search vector store for grounding context and citations")
def search_vector_store(
    body: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Retrieve grounded context chunks and similarity scores for a given query."""
    context_str, citations = global_rag_engine.retrieve_grounding_context(
        body.query, top_k=body.top_k
    )
    return SearchResponse(
        query=body.query,
        grounding_context=context_str,
        citations=[CitationChunk(**c) for c in citations],
    )
