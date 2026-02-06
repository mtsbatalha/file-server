"""
Main FastAPI Application
Entry point for the File Server Management API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from backend.core.config import get_settings
from backend.core.database import init_db

settings = get_settings()

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("Starting File Server Management API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Create default admin user if not exists
    from backend.api.services.user_service import create_default_admin
    try:
        create_default_admin()
        logger.info("Default admin user checked/created")
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")
    
    # Initialize default protocols
    from backend.api.services.protocol_service import initialize_protocols
    try:
        initialize_protocols()
        logger.info("Default protocols initialized")
    except Exception as e:
        logger.error(f"Failed to initialize protocols: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down File Server Management API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-protocol file server management system with web interface",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "File Server Management API",
        "version": settings.app_version,
        "docs": "/docs"
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


# Import and include routers
from backend.api.routes import auth, users, protocols, paths, quotas, logs

app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["Users"])
app.include_router(protocols.router, prefix=f"{settings.api_prefix}/protocols", tags=["Protocols"])
app.include_router(paths.router, prefix=f"{settings.api_prefix}/paths", tags=["Shared Paths"])
app.include_router(quotas.router, prefix=f"{settings.api_prefix}/quotas", tags=["Quotas"])
app.include_router(logs.router, prefix=f"{settings.api_prefix}/logs", tags=["Logs"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
