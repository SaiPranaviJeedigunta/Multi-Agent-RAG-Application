from langchain_core.runnables import RunnablePassthrough
from google.cloud import storage
from typing import List, Dict, Any
import os

class DocumentAgent:
    def __init__(self):
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.client = storage.Client.from_service_account_json(credentials_path)
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.chain = self._create_chain()

    def _create_chain(self):
        return RunnablePassthrough.assign(
            documents=self.list_documents,
            content=self.get_document
        )

    async def list_documents(self, state: Dict[str, Any]) -> List[str]:
        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix="cfai_publications/")
        return [blob.name for blob in blobs if blob.name.endswith('.pdf')]

    async def get_document(self, state: Dict[str, Any]) -> bytes:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(state["document_id"])
        return blob.download_as_bytes()

    def create_node(self):
        return self.chain