"""
Transcription route for handling audio file uploads
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.services.whisper_service import WhisperService
from app.utils.audio_utils import validate_audio_file
from app.schemas.summary import TranscriptionResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Whisper service
whisper_service = WhisperService()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe (MP3, WAV, or raw audio)")
):
    """
    Transcribe an uploaded audio file using Whisper.
    
    Args:
        file: Audio file (MP3, WAV, or raw audio)
        
    Returns:
        TranscriptionResponse: Contains transcript, confidence, and language
    """
    try:
        # Validate the uploaded file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate audio file format
        if not validate_audio_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid audio file format. Supported formats: MP3, WAV, M4A, FLAC"
            )
        
        logger.info(f"Processing audio file: {file.filename}")
        
        # Transcribe the audio
        result = await whisper_service.transcribe(file)
        
        logger.info(f"Transcription completed for {file.filename}")
        
        return TranscriptionResponse(
            transcript=result["transcript"],
            confidence=result.get("confidence", 0.0),
            language=result.get("language", "en"),
            duration=result.get("duration", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/transcribe/status")
async def transcription_status():
    """
    Get the status of the transcription service.
    
    Returns:
        dict: Service status information
    """
    try:
        status = await whisper_service.get_status()
        return {
            "status": "operational",
            "model": status.get("model", "unknown"),
            "provider": status.get("provider", "local"),
            "available": status.get("available", True)
        }
    except Exception as e:
        logger.error(f"Error getting transcription status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        } 