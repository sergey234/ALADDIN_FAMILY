"""
ALADDIN Backend API Server
FastAPI application for subscription management
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers.subscription import router as subscription_router

# Create FastAPI app
app = FastAPI(
    title="ALADDIN Backend API",
    description="Subscription Management System for ALADDIN iOS App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subscription_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ALADDIN Backend API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ALADDIN Backend API",
        "docs": "/docs",
        "health": "/health"
    }

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    print(f"[{request.method}] {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )