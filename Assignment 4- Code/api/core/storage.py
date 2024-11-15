from datetime import datetime
import json
import aiofiles
import os
from typing import Dict, Optional
from ..models import ResearchResult, ResearchSession 

class ResearchStorage:
    def __init__(self):
        self.sessions = {}

    async def save_research_result(self, session_id: str, result: ResearchResult):
        """Save research result to session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'results': [],
                'created_at': datetime.now(),
                'document_id': result.document_id
            }
        
        if len(self.sessions[session_id]['results']) >= 6:
            raise ValueError("Maximum questions reached for this session")
            
        self.sessions[session_id]['results'].append(result.dict())
        self.sessions[session_id]['updated_at'] = datetime.now() 

class SessionStorage:
    def __init__(self, storage_path: str = "data/sessions"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    async def save_session(self, session: ResearchSession):
        """Save session to file"""
        file_path = f"{self.storage_path}/{session.session_id}.json"
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(session.json())

    async def load_session(self, session_id: str) -> Optional[ResearchSession]:
        """Load session from file"""
        file_path = f"{self.storage_path}/{session_id}.json"
        try:
            async with aiofiles.open(file_path, 'r') as f:
                data = await f.read()
                return ResearchSession.parse_raw(data)
        except FileNotFoundError:
            return None 