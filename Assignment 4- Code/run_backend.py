import os
import uvicorn
import logging
import sys
from fastapi.logger import logger
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logging():
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File Handler
    file_handler = RotatingFileHandler(
        'logs/api.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # FastAPI logger
    logger.handlers = []
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def check_dependencies():
    try:
        import pinecone
        from serpapi import GoogleSearch
        from google.cloud import storage
        logger.info("All required dependencies are installed")
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        sys.exit(1)

def main():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Setup logging
    setup_logging()
    
    # Check dependencies
    check_dependencies()

    # Log startup message
    logger.info("Starting Research API Server...")
    
    try:
        # Add debug prints for imports
        logger.info("Starting imports...")
        
        # Import and verify models first
        from api.models import ResearchResult, ArxivResult, WebSearchResult
        logger.info("Models imported successfully")
        
        # Import and initialize Pinecone separately
        logger.info("Initializing Pinecone...")
        from api.core.pinecone_client import init_pinecone
        init_pinecone()  # Initialize Pinecone first
        logger.info("Pinecone initialized successfully")
        
        from api.core.pinecone_client import get_index
        index = get_index()
        logger.info("Pinecone index retrieved successfully")
        
        # Import other components
        logger.info("Importing service components...")
        from api.service import web_search, fetch_arxiv
        logger.info("Service functions imported successfully")
        
        logger.info("Importing main app...")
        from api.main import app
        logger.info("Main app imported successfully")

        # Start server
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            "api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error location: {e.__traceback__.tb_frame.f_code.co_filename}")
        logger.error(f"Error line: {e.__traceback__.tb_lineno}")
        # Print full traceback
        import traceback
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()