import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load .env file from project root
env_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path=env_path)

# API Keys - Load from environment variables only
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = "research-publications-index"  # Constant value
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_KEY")
# Google Cloud Storage - Load from environment
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Constants and Configuration
RESEARCH_SESSION_LIMIT = 6
EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETION_MODEL = "gpt-4-turbo-preview"
VECTOR_DIMENSION = 384
VECTOR_SIMILARITY_THRESHOLD = 0.7
MAX_CONTEXT_LENGTH = 1000

# Validate required environment variables
required_vars = [
    "PINECONE_API_KEY",
    "PINECONE_ENVIRONMENT",
    "OPENAI_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCS_BUCKET_NAME",
    "SERPAPI_KEY"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Log configuration loading
logger.info("Environment configuration loaded successfully")