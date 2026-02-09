"""
Sentri Retail Demo - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import settings
from .db.database import engine, Base
from .api import health, auth, scans, guardian, assistant, demo, gateway


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup - create tables
    Base.metadata.create_all(bind=engine)
    print(f"Starting Sentri Retail Demo API v{settings.VERSION}")
    print(f"Mode: {settings.SENTRI_MODE}")
    
    yield
    
    # Shutdown
    print("Shutting down Sentri Retail Demo API")


# Create FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Retail security and risk management system with AI-powered insights",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(scans.router, prefix="/api/v1/scan", tags=["security-scans"])
app.include_router(guardian.router, prefix="/api/v1/guardian", tags=["guardian-engine"])
app.include_router(assistant.router, prefix="/api/v1/assistant", tags=["ai-assistant"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])
app.include_router(gateway.router, prefix="/api/v1/gateway", tags=["agent-gateway"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentri Retail Demo API",
        "version": settings.VERSION,
        "mode": settings.SENTRI_MODE,
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )