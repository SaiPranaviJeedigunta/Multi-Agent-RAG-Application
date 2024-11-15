from dotenv import load_dotenv
import os

load_dotenv()

def load_config():
    return {
        "backend_url": os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")
    }