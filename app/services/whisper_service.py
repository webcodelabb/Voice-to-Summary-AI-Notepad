"""
Whisper service for audio transcription
Supports both local Whisper and OpenAI Whisper API
"""

import os
import logging
import tempfile
import aiofiles
from typing import Dict, Any, Optional
from fastapi import UploadFile
import whisper
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WhisperService:
    """Service for handling audio transcription using Whisper"""
    
    def __init__(self):
        self.use_openai_whisper = os.getenv("USE_OPENAI_WHISPER", "false").lower() == "true"
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize local Whisper model if not using OpenAI
        self.local_model = None
        if not self.use_openai_whisper:
            try:
                logger.info(f"Loading local Whisper model: {self.whisper_model}")
                self.local_model = whisper.load_model(self.whisper_model)
                logger.info("Local Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load local Whisper model: {str(e)}")
                raise Exception(f"Failed to initialize Whisper model: {str(e)}")
        
        # Initialize OpenAI client if using OpenAI Whisper
        if self.use_openai_whisper:
            if not self.openai_api_key:
                raise Exception("OpenAI API key required when using OpenAI Whisper")
            openai.api_key = self.openai_api_key
            logger.info("OpenAI Whisper API configured")
    
    async def transcribe(self, file: UploadFile) -> Dict[str, Any]:
        """
        Transcribe an audio file using Whisper.
        
        Args:
            file: Uploaded audio file
            
        Returns:
            Dict containing transcript, confidence, language, and duration
        """
        try:
            # Save uploaded file to temporary location
            temp_file = await self._save_uploaded_file(file)
            
            if self.use_openai_whisper:
                return await self._transcribe_with_openai(temp_file)
            else:
                return await self._transcribe_with_local(temp_file)
                
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
        finally:
            # Clean up temporary file
            if 'temp_file' in locals():
                await self._cleanup_temp_file(temp_file)
    
    async def _save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
            temp_path = temp_file.name
            temp_file.close()
            
            # Write uploaded content to temporary file
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"Saved uploaded file to: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise Exception(f"Failed to save uploaded file: {str(e)}")
    
    async def _transcribe_with_openai(self, file_path: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            logger.info("Using OpenAI Whisper API for transcription")
            
            with open(file_path, 'rb') as audio_file:
                response = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    response_format="verbose_json"
                )
            
            # Extract information from response
            transcript = response.get("text", "")
            language = response.get("language", "en")
            duration = response.get("duration", 0.0)
            
            # Calculate confidence (OpenAI doesn't provide confidence scores)
            confidence = 0.95  # Default confidence for OpenAI
            
            logger.info(f"OpenAI transcription completed. Language: {language}, Duration: {duration}s")
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": language,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"OpenAI transcription failed: {str(e)}")
            raise Exception(f"OpenAI transcription failed: {str(e)}")
    
    async def _transcribe_with_local(self, file_path: str) -> Dict[str, Any]:
        """Transcribe using local Whisper model"""
        try:
            logger.info("Using local Whisper model for transcription")
            
            # Transcribe audio
            result = self.local_model.transcribe(file_path)
            
            # Extract information from result
            transcript = result.get("text", "").strip()
            language = result.get("language", "en")
            segments = result.get("segments", [])
            
            # Calculate average confidence
            if segments:
                confidences = [segment.get("avg_logprob", 0) for segment in segments]
                confidence = sum(confidences) / len(confidences) if confidences else 0.0
                # Convert log probability to confidence (0-1 scale)
                confidence = max(0.0, min(1.0, (confidence + 1) / 2))
            else:
                confidence = 0.8  # Default confidence
            
            # Calculate duration from segments
            duration = 0.0
            if segments:
                duration = segments[-1].get("end", 0.0)
            
            logger.info(f"Local transcription completed. Language: {language}, Duration: {duration}s")
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": language,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Local transcription failed: {str(e)}")
            raise Exception(f"Local transcription failed: {str(e)}")
    
    async def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary file {file_path}: {str(e)}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the Whisper service"""
        try:
            if self.use_openai_whisper:
                return {
                    "provider": "openai",
                    "model": "whisper-1",
                    "available": True,
                    "api_key_configured": bool(self.openai_api_key)
                }
            else:
                return {
                    "provider": "local",
                    "model": self.whisper_model,
                    "available": self.local_model is not None,
                    "model_loaded": self.local_model is not None
                }
        except Exception as e:
            logger.error(f"Error getting Whisper status: {str(e)}")
            return {
                "provider": "unknown",
                "model": "unknown",
                "available": False,
                "error": str(e)
            } 