"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum

class SummaryStyle(str, Enum):
    """Available summary styles"""
    BULLET_POINTS = "bullet_points"
    PARAGRAPH = "paragraph"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"

class SummaryRequest(BaseModel):
    """Request model for text summarization"""
    
    text: str = Field(..., description="Text to be summarized", min_length=10)
    max_length: int = Field(150, description="Maximum length of summary in words", ge=10, le=500)
    style: SummaryStyle = Field(SummaryStyle.BULLET_POINTS, description="Summary style")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('max_length')
    def validate_max_length(cls, v):
        if v < 10:
            raise ValueError('Maximum length must be at least 10 words')
        if v > 500:
            raise ValueError('Maximum length cannot exceed 500 words')
        return v

class SummaryResponse(BaseModel):
    """Response model for text summarization"""
    
    summary: str = Field(..., description="Generated summary")
    word_count: int = Field(..., description="Number of words in summary", ge=0)
    original_length: int = Field(..., description="Length of original text", ge=0)
    style: SummaryStyle = Field(..., description="Style used for summarization")
    model_used: str = Field(..., description="Model used for summarization")

class TranscriptionResponse(BaseModel):
    """Response model for audio transcription"""
    
    transcript: str = Field(..., description="Transcribed text from audio")
    confidence: float = Field(..., description="Confidence score of transcription", ge=0.0, le=1.0)
    language: str = Field(..., description="Detected language code")
    duration: float = Field(..., description="Duration of audio in seconds", ge=0.0)

class BatchSummaryRequest(BaseModel):
    """Request model for batch summarization"""
    
    texts: list[SummaryRequest] = Field(..., description="List of texts to summarize", max_items=10)
    
    @validator('texts')
    def validate_texts(cls, v):
        if not v:
            raise ValueError('At least one text must be provided')
        if len(v) > 10:
            raise ValueError('Maximum 10 texts allowed for batch processing')
        return v

class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")

class HealthResponse(BaseModel):
    """Health check response model"""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(None, description="API version")
    timestamp: Optional[str] = Field(None, description="Current timestamp")

class ServiceStatusResponse(BaseModel):
    """Service status response model"""
    
    status: str = Field(..., description="Service status")
    provider: str = Field(..., description="Service provider")
    model: str = Field(..., description="Model being used")
    available: bool = Field(..., description="Whether service is available")
    error: Optional[str] = Field(None, description="Error message if any") 