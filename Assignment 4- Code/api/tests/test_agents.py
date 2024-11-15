import pytest
from ..agents.rag_agent import RAGAgent
from ..agents.arxiv_agent import ArxivAgent
from ..agents.web_agent import WebAgent
from ..agents.document_agent import DocumentAgent
from ..models import ArxivResult, WebSearchResult

@pytest.mark.asyncio
async def test_rag_agent():
    """Test RAG agent functionality"""
    agent = RAGAgent()
    result = await agent.execute_rag(
        query="What are the key findings?",
        document_id="test_doc"
    )
    
    assert result is not None
    assert "answer" in result
    assert "context_summary" in result
    assert result["document_id"] == "test_doc"

@pytest.mark.asyncio
async def test_arxiv_agent():
    """Test ArXiv agent search capability"""
    agent = ArxivAgent()
    results = await agent.search_papers("machine learning")
    
    assert isinstance(results, list)
    assert len(results) <= 5  # Max results setting
    if results:
        assert isinstance(results[0], ArxivResult)
        assert all(required in results[0].dict() 
                  for required in ["title", "summary", "published"])

@pytest.mark.asyncio
async def test_web_agent():
    """Test web search agent"""
    agent = WebAgent()
    results = await agent.search_web("artificial intelligence trends")
    
    assert isinstance(results, list)
    assert len(results) <= 5  # Max results setting
    if results:
        assert isinstance(results[0], WebSearchResult)
        assert all(required in results[0].dict() 
                  for required in ["title", "snippet", "link"])

@pytest.mark.asyncio
async def test_document_agent():
    """Test document agent"""
    agent = DocumentAgent()
    documents = await agent.list_documents()
    
    assert isinstance(documents, list)
    assert all(doc.endswith('.pdf') for doc in documents)

@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling"""
    agent = RAGAgent()
    
    # Test with invalid document
    with pytest.raises(ValueError):
        await agent.execute_rag("test query", "nonexistent_doc")
    
    # Test with empty query
    with pytest.raises(ValueError):
        await agent.execute_rag("", "test_doc") 