import os
import sys
 
# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
 
# Now you can import from api
from api.core.pinecone_client import init_pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google.cloud import storage
import tempfile
from tqdm import tqdm
import logging
 
# Set up logging at the very start of the file
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
logger.debug("Script starting...")
 
async def load_documents_from_gcs():
    """Load documents from Google Cloud Storage"""
    try:
        # Initialize GCS client
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        storage_client = storage.Client.from_service_account_json(credentials_path)
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        bucket = storage_client.bucket(bucket_name)
 
        # List all PDF files in the bucket
        blobs = bucket.list_blobs(prefix="cfai_publications/")
        pdf_blobs = [blob for blob in blobs if blob.name.endswith('.pdf')]
 
        documents = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
 
        for blob in tqdm(pdf_blobs, desc="Loading documents"):
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                blob.download_to_filename(temp_file.name)
               
                # Load and split the PDF
                loader = PyPDFLoader(temp_file.name)
                doc_pages = loader.load()
               
                # Add source metadata
                for page in doc_pages:
                    page.metadata["source"] = blob.name
               
                # Split into chunks
                chunks = text_splitter.split_documents(doc_pages)
                documents.extend(chunks)
               
                # Clean up temp file
                os.unlink(temp_file.name)
 
        return documents
 
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        raise
 
async def reindex_documents():
    """Reindex documents with correct embedding dimensions"""
    try:
        # Initialize embeddings with correct model
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
       
        # Initialize Pinecone
        index = init_pinecone()
       
        # Load documents from GCS
        logger.info("Loading documents from GCS...")
        documents = await load_documents_from_gcs()
        logger.info(f"Loaded {len(documents)} document chunks")
       
        # Create embeddings and upsert to Pinecone
        logger.info("Starting indexing process...")
        for doc in tqdm(documents, desc="Indexing documents"):
            try:
                # Generate embedding
                embedding = await embeddings.aembed_query(doc.page_content)
               
                # Prepare metadata
                metadata = {
                    "text": doc.page_content,
                    "document_id": doc.metadata.get("source", ""),
                    "page": doc.metadata.get("page", 0)
                }
               
                # Upsert to Pinecone
                index.upsert(
                    vectors=[{
                        "id": f"doc_{hash(doc.page_content)}",
                        "values": embedding,
                        "metadata": metadata
                    }]
                )
            except Exception as e:
                logger.error(f"Error indexing document chunk: {str(e)}")
                continue
 
        logger.info("Indexing completed successfully")
 
    except Exception as e:
        logger.error(f"Reindexing failed: {str(e)}")
        raise
 
if __name__ == "__main__":
    logger.debug("Entering main block...")
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
   
    # Verify required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GCS_BUCKET_NAME"
    ]
   
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
   
    # Run the reindexing
    import asyncio
    asyncio.run(reindex_documents())
 