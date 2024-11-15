import requests
from utils.config import load_config
import logging
from urllib.parse import quote
 
logger = logging.getLogger(__name__)
config = load_config()
BASE_URL = config['backend_url']
 
def fetch_documents():
    try:
        response = requests.get(f"{BASE_URL}/documents")
        response.raise_for_status()
        return response.json().get('available_documents', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching documents: {str(e)}")
        return {'error': str(e), 'available_documents': []}
 
def search_arxiv(query):
    try:
        response = requests.get(f"{BASE_URL}/arxiv_search", params={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching arxiv: {str(e)}")
        return {'error': str(e), 'results': []}
 
def search_web(query):
    try:
        response = requests.get(f"{BASE_URL}/web_search", params={"query": query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching web: {str(e)}")
        return {'error': str(e), 'results': []}
 
def conduct_research(document_id, query):
    try:
        # Remove leading/trailing slashes and normalize path
        clean_doc_id = document_id.strip('/')
       
        # Log original and cleaned document IDs
        logger.info(f"Original document ID: {document_id}")
        logger.info(f"Cleaned document ID: {clean_doc_id}")
       
        # Make the request
        response = requests.post(
            f"{BASE_URL}/research",  # Remove document_id from URL
            json={
                "document_id": clean_doc_id,
                "query": query,
                "use_rag": True,
                "use_arxiv": True,
                "use_web": True
            }
        )
       
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error conducting research: {str(e)}")
        return {
            'error': str(e),
            'combined_analysis': f"Error: {str(e)}",
            'result': None
        }
 
def get_research_session(document_id):
    try:
        # Encode document ID for session requests as well
        encoded_doc_id = quote(document_id, safe='')
        response = requests.get(f"{BASE_URL}/research/session/{encoded_doc_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting research session: {str(e)}")
        return {'error': str(e), 'session': None}
 
 
 