import os
import logging
from google.cloud import storage
import requests
from serpapi import GoogleSearch
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from langchain_core.tools import tool
from api.core.pinecone_client import get_index
from api.models import ResearchResult
from urllib.parse import quote, unquote
import re
 
load_dotenv()
 
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
index = get_index()
 
# GCS setup
bucket_name = os.getenv("GCS_BUCKET_NAME")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
file_paths = [
    "cfai_publications/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios.pdf",
    "cfai_publications/An Introduction to Alternative Credit/An Introduction to Alternative Credit.pdf"
]
 
# Initialize GCS client with better error handling
try:
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
   
    # Resolve the path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_credentials_path = os.path.join(project_root, credentials_path)
   
    if not os.path.exists(full_credentials_path):
        raise FileNotFoundError(
            f"Google Cloud credentials file not found at: {full_credentials_path}"
        )
   
    gcs_client = storage.Client.from_service_account_json(full_credentials_path)
    logger.info("GCS client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GCS client: {str(e)}")
    raise
 
# Document Selection Tool
@tool("select_document")
def get_available_documents_from_gcs():
    """Fetches the specified documents from Google Cloud Storage if they exist."""
    try:
        logger.info("Fetching specified documents from GCS.")
       
        if not bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable not set")
           
        if not gcs_client:
            raise ValueError("GCS client not properly initialized")
           
        bucket = gcs_client.bucket(bucket_name)
        available_docs = []
 
        if not bucket.exists():
            raise ValueError(f"Bucket {bucket_name} does not exist")
 
        # Normalize document paths
        for file_path in file_paths:
            try:
                # Normalize the path
                normalized_path = re.sub(r'[\\/:*?"<>|]', '_', file_path)
                blob = bucket.blob(file_path)
                if blob.exists():
                    logger.info(f"Document found: {file_path}")
                    # Store the original path
                    available_docs.append(file_path)
                else:
                    logger.warning(f"Document not found in GCS: {file_path}")
            except Exception as blob_error:
                logger.error(f"Error checking blob {file_path}: {str(blob_error)}")
 
        if not available_docs:
            logger.warning("No documents found in GCS")
            return []
 
        return available_docs
 
    except Exception as e:
        logger.error(f"Error in get_available_documents_from_gcs: {str(e)}")
        raise ValueError(f"Failed to fetch documents: {str(e)}")
 
# Add this helper function
def normalize_document_path(doc_path: str) -> str:
    """Normalize document path for consistent handling"""
    # Remove any double slashes and normalize separators
    normalized = re.sub(r'[/\\]+', '/', doc_path)
    # Remove .pdf extension if present
    normalized = normalized.replace('.pdf', '')
    return normalized
 
# Arxiv Fetch Function
@tool("fetch_arxiv")
def fetch_arxiv(query: str):
    """Fetches research papers from ArXiv based on a query."""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
    response = requests.get(url)
    if response.status_code != 200:
        return "Error fetching data from Arxiv."
 
    root = ET.fromstring(response.content)
    results = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
        published = entry.find("{http://www.w3.org/2005/Atom}published").text
        authors = [
            author.find("{http://www.w3.org/2005/Atom}name").text
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
 
        results.append({
            "title": title,
            "summary": summary,
            "published": published,
            "authors": authors,
            "link": link
        })
    return results
 
# Web Search Function using SerpAPI
serpapi_api_key = os.getenv("SERPAPI_KEY")
 
@tool("web_search")
def web_search(query: str):
    """Performs a Google search for general knowledge queries using SerpAPI."""
    search = GoogleSearch({
        "q": query,
        "num": 5,
        "engine": "google",
        "api_key": serpapi_api_key
    })
    results = search.get_dict().get("organic_results", [])
    return [{
        "title": x["title"],
        "snippet": x["snippet"],
        "link": x["link"]
    } for x in results]
 
@tool("validate_processed_document")
async def validate_document_processing(document_id: str):
    """Add error handling for missing documents"""
    try:
        response = index.fetch([document_id])
        if not response.vectors:
            logger.warning(f"Document {document_id} not found in Pinecone")
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating document: {str(e)}")
        return False
 
async def get_document(self, document_id: str) -> bytes:
    """Fetch document content from GCS"""
    try:
        logger.info(f"Fetching document: {document_id}")
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(document_id)
       
        if not blob.exists():
            logger.error(f"Document not found: {document_id}")
            raise ValueError(f"Document not found: {document_id}")
           
        return blob.download_as_bytes()
       
    except Exception as e:
        logger.error(f"Error fetching document {document_id}: {str(e)}")
        raise
 