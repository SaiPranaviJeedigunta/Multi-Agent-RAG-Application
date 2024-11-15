import os
from pinecone import Pinecone
from dotenv import load_dotenv
import logging
 
logger = logging.getLogger(__name__)
 
# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "research-publications-index"
 
# Global index instance
index = None
 
def init_pinecone():
    """Initialize Pinecone client and get index"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
       
        # Get the index with 384 dimensions
        index = pc.Index(INDEX_NAME)
        logger.info("Pinecone initialization successful")
        return index
    except Exception as e:
        logger.error(f"Pinecone initialization error: {str(e)}")
        raise
 
def get_index():
    """Get the Pinecone index instance"""
    global index
    if index is None:
        index = init_pinecone()
    return index
 