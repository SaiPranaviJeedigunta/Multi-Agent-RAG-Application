from google.cloud import storage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch bucket name from environment variable
bucket_name = os.getenv("GCS_BUCKET_NAME")

# Check if bucket name is loaded correctly
if not bucket_name:
    raise ValueError("Bucket name not found. Ensure GCS_BUCKET_NAME is set in .env file.")

print("Bucket name:", bucket_name)

# Initialize the Google Cloud Storage client
client = storage.Client()
bucket = client.bucket(bucket_name)

# List of specific files you need to download
file_paths = [
    "cfai_publications/The Economics of Private Equity: A Critical Review/The Economics of Private Equity: A Critical Review.pdf",
    "cfai_publications/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios.pdf",
    "cfai_publications/An Introduction to Alternative Credit/An Introduction to Alternative Credit.pdf"
]

# Function to download specific documents to the current directory
def download_documents_from_gcs(file_paths):
    current_directory = os.getcwd()  # Get the current directory path
    
    for file_path in file_paths:
        blob = bucket.blob(file_path)
        
        # Get the filename from the full path and set the local path in the current directory
        local_file_path = os.path.join(current_directory, os.path.basename(file_path))
        
        # Download the document
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {file_path} to {local_file_path}")

# Download the specified documents
download_documents_from_gcs(file_paths)
