# routers.py
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, Dict, Union
from .models import DocumentResponse, ArxivResult, WebSearchResult, ResearchResult, ResearchSession
from .service import get_available_documents_from_gcs, fetch_arxiv, web_search
from .graphs.research_graph import research_graph
from .core.session_manager import research_session_manager
from datetime import datetime
import logging
from fastapi.responses import StreamingResponse
from .utils.pdf_export import ResearchPDFExporter
from .utils.codelabs_export import CodelabsExporter
from .core.middleware import QueryValidator
from urllib.parse import unquote
from pydantic import BaseModel
 
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
 
router = APIRouter()
 
# Add this class at the top with your other imports
class ResearchRequest(BaseModel):
    document_id: str
    query: str
    use_rag: bool = True
    use_arxiv: bool = True
    use_web: bool = True
 
@router.get("/documents", response_model=DocumentResponse)
async def select_documents():
    """Fetch available documents from GCS."""
    try:
        # Call the tool with invoke, passing an empty dictionary as `tool_input`
        documents = get_available_documents_from_gcs.invoke({})
        if documents is None:
            raise HTTPException(status_code=500, detail="Error fetching documents from GCS.")
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found in GCS.")
        return {"available_documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.get("/arxiv_search", response_model=list[ArxivResult])
async def arxiv_search(query: str):
    """Search for ArXiv papers based on a query."""
    results = fetch_arxiv(query)
    if not results or isinstance(results, str):
        raise HTTPException(status_code=500, detail="Error fetching Arxiv results")
    return results
 
@router.get("/web_search", response_model=list[WebSearchResult])
async def perform_web_search(query: str):
    """Perform a web search using SerpAPI."""
    results = web_search(query)
    if not results:
        raise HTTPException(status_code=500, detail="No results found")
    return results
 
@router.post("/research",
    response_model=Dict[str, Union[str, ResearchResult]]
)
async def conduct_research(
    request: ResearchRequest = Body(...),
    validator: QueryValidator = Depends()
):
    """Conduct research on a specific document."""
    try:
        # Log the incoming request
        logger.info(f"Received research request: {request}")
 
        # Validate document exists
        docs = await get_available_documents_from_gcs.ainvoke({})
        if not docs:
            logger.error("No documents found in storage")
            raise HTTPException(
                status_code=500,
                detail="Error accessing document storage"
            )
 
        # Find exact match for document
        if request.document_id not in docs:
            logger.error(f"Document not found: {request.document_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {request.document_id}"
            )
 
        # Execute research
        logger.info(f"Starting research for document: {request.document_id}")
        try:
            results = await research_graph.execute(
                document_id=request.document_id,
                query=request.query,
                use_rag=request.use_rag,
                use_arxiv=request.use_arxiv,
                use_web=request.use_web
            )
        except Exception as e:
            logger.error(f"Research execution error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Research execution failed: {str(e)}"
            )
 
        if not results:
            raise HTTPException(
                status_code=500,
                detail="Research execution failed to return results"
            )
 
        research_result = ResearchResult(
            document_id=request.document_id,
            query=request.query,
            rag_response=results.get("rag"),
            arxiv_results=results.get("arxiv"),
            web_results=results.get("web"),
            combined_analysis=results.get("combined"),
            timestamp=datetime.now()
        )
 
        session_id = await research_session_manager.add_result(
            request.document_id,
            research_result
        )
       
        return {
            "session_id": session_id,
            "result": research_result
        }
 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error conducting research: {str(e)}"
        )
 
@router.get("/research/session/{document_id}", response_model=ResearchSession)
async def get_research_session(document_id: str):
    """Get or create a research session for a document"""
    try:
        session = await research_session_manager.get_session(document_id)
        if len(session.questions) >= 6:
            raise HTTPException(
                status_code=400,
                detail="Maximum questions (6) reached for this document"
            )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@router.post("/research/export/{session_id}/pdf")
async def export_pdf(session_id: str):
    """Export research session as PDF"""
    try:
        session = await research_session_manager.get_session(session_id)
        pdf_exporter = ResearchPDFExporter()
        pdf_bytes = pdf_exporter.export_session(session)
       
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment;filename=research_{session_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@router.post("/research/export/{session_id}/codelabs")
async def export_codelabs(session_id: str):
    """Export research session in Codelabs format"""
    try:
        session = await research_session_manager.get_session(session_id)
        codelabs_exporter = CodelabsExporter()
        return codelabs_exporter.export_session(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 