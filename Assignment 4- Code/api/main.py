from fastapi import FastAPI
from .routers import router  # Update relative import
from fastapi.middleware.cors import CORSMiddleware
from .core.middleware import RateLimitMiddleware, ErrorHandlingMiddleware
from fastapi.openapi.utils import get_openapi
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Research API",
    description="API for multi-agent research system",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up...")
    # Initialize your components here
    logger.info("All components initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down...")

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Include router
app.include_router(
    router,
    prefix="/api/v1",
    tags=["research"]
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Research API",
        version="1.0.0",
        description="API for multi-agent research system",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
