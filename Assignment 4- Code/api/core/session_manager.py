from datetime import datetime
import uuid
from typing import Dict, Optional
from ..models import ResearchSession, ResearchResult
from .storage import SessionStorage
import logging

logger = logging.getLogger(__name__)

class ResearchSessionManager:
    def __init__(self):
        logger.info("Initializing Research Session Manager...")
        self.sessions: Dict[str, ResearchSession] = {}
        self.storage = SessionStorage()
        
    async def create_session(self, document_id: str) -> ResearchSession:
        """Create a new research session"""
        session_id = str(uuid.uuid4())
        session = ResearchSession(
            session_id=session_id,
            document_id=document_id,
            questions=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.sessions[session_id] = session
        return session

    async def get_session(self, document_id: str) -> ResearchSession:
        """Get or create a session for a document"""
        try:
            # Find existing session for document
            session = next(
                (s for s in self.sessions.values() if s.document_id == document_id),
                None
            )
            
            if not session:
                logger.info(f"Creating new session for document: {document_id}")
                session = await self.create_session(document_id)
                
            return session
        except Exception as e:
            logger.error(f"Error getting session for document {document_id}: {str(e)}")
            raise
    
    async def add_question(self, session_id: str, result: ResearchResult):
        """Add a question to existing session"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
            
        session = self.sessions[session_id]
        if len(session.questions) >= 6:
            raise ValueError("Maximum questions reached")
            
        session.questions.append(result)
        session.updated_at = datetime.now()

    async def add_result(self, document_id: str, result: ResearchResult) -> str:
        """Add research result to session by document ID"""
        try:
            session = await self.get_session(document_id)
            
            if len(session.questions) >= 6:
                raise ValueError("Maximum questions reached for this document")
                
            session.questions.append(result)
            session.updated_at = datetime.now()
            
            logger.info(f"Added result to session {session.session_id} for document {document_id}")
            return session.session_id
        except Exception as e:
            logger.error(f"Error adding result for document {document_id}: {str(e)}")
            raise

    async def persist_session(self, session_id: str):
        """Add session persistence"""
        try:
            session = self.sessions.get(session_id)
            if session:
                await self.storage.save_session(session)
                logger.info(f"Session {session_id} persisted successfully")
        except Exception as e:
            logger.error(f"Error persisting session {session_id}: {str(e)}")

    async def load_session(self, session_id: str) -> Optional[ResearchSession]:
        """Load session from storage if not in memory"""
        if session_id not in self.sessions:
            session = await self.storage.load_session(session_id)
            if session:
                self.sessions[session_id] = session
        return self.sessions.get(session_id)

research_session_manager = ResearchSessionManager() 