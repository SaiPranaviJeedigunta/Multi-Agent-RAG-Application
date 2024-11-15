from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    available_documents: List[str]

class ArxivResult(BaseModel):
    title: str
    summary: str
    published: str
    authors: List[str]
    link: str

class WebSearchResult(BaseModel):
    title: str
    snippet: str
    link: str

class ResearchResult(BaseModel):
    document_id: str
    query: str
    rag_response: Optional[str] = None
    arxiv_results: Optional[List[ArxivResult]] = None
    web_results: Optional[List[WebSearchResult]] = None
    combined_analysis: str
    timestamp: datetime = datetime.now()

class ResearchSession(BaseModel):
    session_id: str
    document_id: str
    questions: List[ResearchResult]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
