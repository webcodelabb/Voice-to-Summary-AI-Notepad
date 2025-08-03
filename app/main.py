"""
Voice-to-Summary AI Notepad Backend
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import transcribe, summarize

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Voice-to-Summary AI Notepad API",
    description="A production-ready backend for audio transcription and AI summarization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcribe.router, prefix="/api/v1", tags=["transcription"])
app.include_router(summarize.router, prefix="/api/v1", tags=["summarization"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Voice-to-Summary AI Notepad API",
        "version": "1.0.0",
        "endpoints": {
            "transcribe": "/api/v1/transcribe",
            "summarize": "/api/v1/summarize",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice-summary-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 