from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import re
from typing import Dict, List
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}
        logger.info(f"RateLimitMiddleware initialized with {max_requests} requests per {window_seconds} seconds")

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old requests
        if client_ip in self.requests:
            original_count = len(self.requests[client_ip])
            self.requests[client_ip] = [
                ts for ts in self.requests[client_ip]
                if now - ts < timedelta(seconds=self.window_seconds)
            ]
            cleaned_count = len(self.requests[client_ip])
            if original_count != cleaned_count:
                logger.debug(f"Cleaned {original_count - cleaned_count} old requests for {client_ip}")
        
        # Check rate limit
        if len(self.requests.get(client_ip, [])) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Add request
        self.requests.setdefault(client_ip, []).append(now)
        logger.debug(f"Request added for {client_ip}. Total requests: {len(self.requests[client_ip])}")
        
        return await call_next(request)

    async def cleanup_old_requests(self):
        """Add periodic cleanup"""
        now = datetime.now()
        cleaned_ips = 0
        for ip in list(self.requests.keys()):
            original_count = len(self.requests[ip])
            self.requests[ip] = [
                ts for ts in self.requests[ip]
                if (now - ts).total_seconds() < self.window_seconds
            ]
            if not self.requests[ip]:
                del self.requests[ip]
                cleaned_ips += 1
        if cleaned_ips > 0:
            logger.info(f"Cleaned up requests for {cleaned_ips} IPs")

class QueryValidator:
    @staticmethod
    def validate_query(query: str) -> bool:
        """Validate research query"""
        if not query or len(query.strip()) < 10:
            logger.warning(f"Query rejected: too short - {len(query.strip())} chars")
            return False
        if len(query) > 500:
            logger.warning(f"Query rejected: too long - {len(query)} chars")
            return False
        if not re.match(r'^[\w\s\?\.,\-\'\"]+$', query):
            logger.warning("Query rejected: contains invalid characters")
            return False
        logger.debug("Query validated successfully")
        return True 

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            error_msg = f"Unhandled error during {request.method} {request.url.path}: {str(e)}"
            logger.error(error_msg)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(e)}
            )