import os
import json
import glob
import logging
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize Pinecone with environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = "us-east-1"
pc = Pinecone(api_key=pinecone_api_key)

# Define Pinecone index parameters
index_name = "enhanced-publications-index"
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dimension = embedding_model.get_sentence_embedding_dimension()

# Initialize CLIP model and processor for image embeddings
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_embedding_dim = clip_model.config.projection_dim

# Create the Pinecone index if it doesn't already exist
if index_name not in pc.list_indexes().names():
    logging.info(f"Creating Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,  # Ensure this matches your chosen dimension (384)
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region=pinecone_env)
    )

# Connect to the index
index = pc.Index(index_name)
logging.info(f"Connected to Pinecone index: {index_name}")

# Path to the directory with parsed content
parsed_content_dir = "parsed_content"

# Function to chunk text into smaller parts if it exceeds max token length
def chunk_text(text, max_length=512):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Step 1: Process each JSON file containing chunked text data
for json_file_path in glob.glob(os.path.join(parsed_content_dir, "*_chunks.json")):
    with open(json_file_path, 'r') as f:
        chunks = json.load(f)
        
        for chunk in chunks:
            try:
                # Extract text and metadata
                text_content = chunk['text']
                pdf_filename = chunk['meta']['origin']['filename']
                page_no = chunk['meta']['doc_items'][0]['prov'][0].get("page_no")
                
                # Chunk large text content
                for text_chunk in chunk_text(text_content):
                    embedding = embedding_model.encode(text_chunk).tolist()
                    
                    # Metadata for each chunk
                    metadata = {
                        "document": chunk['document'],
                        "chunk_id": chunk['chunk_id'],
                        "page_no": page_no,
                        "type": "text_chunk",
                        "pdf_filename": pdf_filename
                    }
                    
                    # Upload the chunk to Pinecone
                    index.upsert([(f"{chunk['document']}_{chunk['chunk_id']}", embedding, metadata)])
                    logging.info(f"Uploaded text chunk {chunk['chunk_id']} from document '{chunk['document']}'")
            
            except Exception as e:
                logging.error(f"Failed to process text chunk in {json_file_path}: {e}")

# Step 2: Embed and upload table data with pdf_filename reference
for table_csv_path in glob.glob(os.path.join(parsed_content_dir, "*-table-*.csv")):
    try:
        doc_filename = Path(table_csv_path).stem.split('-table')[0]
        
        # Read table data and embed
        table_data = pd.read_csv(table_csv_path).to_string()
        table_embedding = embedding_model.encode(table_data).tolist()
        
        # Create metadata for table
        metadata = {
            "document": doc_filename,
            "type": "table",
            "filename": os.path.basename(table_csv_path),
            "pdf_filename": f"{doc_filename}.pdf"
        }
        
        # Upsert table data into Pinecone
        index.upsert([(f"{doc_filename}_table", table_embedding, metadata)])
        logging.info(f"Uploaded table data from '{table_csv_path}'")
    
    except Exception as e:
        logging.error(f"Failed to process table file {table_csv_path}: {e}")

# Step 3: Embed and upload images with pdf_filename reference using CLIP embeddings
for image_path in glob.glob(os.path.join(parsed_content_dir, "*-page-*.png")) + glob.glob(os.path.join(parsed_content_dir, "*-picture-*.png")):
    try:
        doc_filename = Path(image_path).stem.split('-page')[0].split('-picture')[0]
        
        # Load and preprocess image for CLIP
        image = Image.open(image_path)
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_embedding = clip_model.get_image_features(**inputs).squeeze().tolist()
        
        # Truncate the image embedding to match text embedding dimension
        truncated_image_embedding = image_embedding[:embedding_dimension]
        
        # Image metadata
        metadata = {
            "document": doc_filename,
            "type": "image",
            "filename": os.path.basename(image_path),
            "pdf_filename": f"{doc_filename}.pdf"
        }
        
        # Upsert image data into Pinecone
        index.upsert([(f"{doc_filename}_{Path(image_path).stem}", truncated_image_embedding, metadata)])
        logging.info(f"Uploaded image data for '{image_path}'")
    
    except Exception as e:
        logging.error(f"Failed to process image file {image_path}: {e}")

logging.info("Data successfully embedded and uploaded to Pinecone.")
