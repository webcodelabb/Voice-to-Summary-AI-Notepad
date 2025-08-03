"""
Audio utilities for validation and preprocessing
"""

import os
import logging
from typing import List, Tuple
from fastapi import UploadFile
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {
    'audio/mpeg': '.mp3',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/mp4': '.m4a',
    'audio/x-m4a': '.m4a',
    'audio/flac': '.flac',
    'audio/x-flac': '.flac',
    'audio/ogg': '.ogg',
    'audio/webm': '.webm'
}

# File extensions that are supported
SUPPORTED_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm']

def validate_audio_file(file: UploadFile) -> bool:
    """
    Validate if the uploaded file is a supported audio format.
    
    Args:
        file: Uploaded file to validate
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        # Check if file has a name
        if not file.filename:
            logger.warning("No filename provided")
            return False
        
        # Check file extension
        file_extension = os.path.splitext(file.filename.lower())[1]
        if file_extension not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Unsupported file extension: {file_extension}")
            return False
        
        # Check content type if available
        if file.content_type:
            if file.content_type not in SUPPORTED_FORMATS:
                logger.warning(f"Unsupported content type: {file.content_type}")
                return False
        
        # Check file size (max 50MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes")
            return False
        
        if file_size == 0:
            logger.warning("Empty file")
            return False
        
        logger.info(f"Audio file validation passed: {file.filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error validating audio file: {str(e)}")
        return False

async def preprocess_audio(file: UploadFile) -> Tuple[str, str]:
    """
    Preprocess audio file for transcription.
    Converts to appropriate format and saves to temporary file.
    
    Args:
        file: Uploaded audio file
        
    Returns:
        Tuple[str, str]: (temp_file_path, original_format)
    """
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        # Read uploaded file content
        content = await file.read()
        
        # Save to temporary file first
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        temp_input.write(content)
        temp_input.close()
        
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(temp_input.name)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Normalize audio levels
            audio = audio.normalize()
            
            # Export as WAV for better compatibility
            audio.export(temp_path, format="wav")
            
            logger.info(f"Audio preprocessing completed: {file.filename} -> {temp_path}")
            return temp_path, "wav"
            
        finally:
            # Clean up temporary input file
            if os.path.exists(temp_input.name):
                os.unlink(temp_input.name)
                
    except Exception as e:
        logger.error(f"Error preprocessing audio: {str(e)}")
        raise Exception(f"Audio preprocessing failed: {str(e)}")

def get_audio_duration(file_path: str) -> float:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        logger.error(f"Error getting audio duration: {str(e)}")
        return 0.0

def is_audio_file_empty(file_path: str) -> bool:
    """
    Check if audio file is empty or has no audible content.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        bool: True if file is empty, False otherwise
    """
    try:
        audio = AudioSegment.from_file(file_path)
        
        # Check if duration is very short (less than 0.5 seconds)
        if len(audio) < 500:
            return True
        
        # Check if audio is silent (very low volume)
        if audio.dBFS < -50:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if audio is empty: {str(e)}")
        return True

def get_supported_formats() -> List[str]:
    """
    Get list of supported audio formats.
    
    Returns:
        List[str]: List of supported file extensions
    """
    return SUPPORTED_EXTENSIONS.copy()

def get_max_file_size() -> int:
    """
    Get maximum allowed file size in bytes.
    
    Returns:
        int: Maximum file size in bytes
    """
    return 50 * 1024 * 1024  # 50MB 