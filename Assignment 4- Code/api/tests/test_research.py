import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..core.session_manager import research_session_manager

client = TestClient(app)

@pytest.mark.asyncio
async def test_research_flow():
    # Test document selection
    response = client.get("/documents")
    assert response.status_code == 200
    documents = response.json()["available_documents"]
    assert len(documents) > 0
    
    # Test research
    doc_id = documents[0]
    response = client.post(
        f"/research/{doc_id}",
        json={
            "query": "What are the main findings?",
            "use_rag": True,
            "use_arxiv": True,
            "use_web": True
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "session_id" in result
    assert "result" in result

@pytest.mark.asyncio
async def test_session_limits():
    doc_id = "test_doc"
    
    # Add maximum questions
    for i in range(6):
        response = client.post(
            f"/research/{doc_id}",
            json={"query": f"Question {i}"}
        )
        assert response.status_code == 200
    
    # Try to add one more
    response = client.post(
        f"/research/{doc_id}",
        json={"query": "Extra question"}
    )
    assert response.status_code == 400 