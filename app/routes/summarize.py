"""
Summarization route for handling text summarization requests
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.services.llm_service import LLMService
from app.schemas.summary import SummaryRequest, SummaryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LLM service
llm_service = LLMService()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequest):
    """
    Summarize the provided text using AI models.
    
    Args:
        request: SummaryRequest containing text and parameters
        
    Returns:
        SummaryResponse: Contains summary, word count, and metadata
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) < 10:
            raise HTTPException(status_code=400, detail="Text too short for summarization")
        
        logger.info(f"Summarizing text of length: {len(request.text)}")
        
        # Generate summary
        result = await llm_service.summarize(
            text=request.text,
            max_length=request.max_length,
            style=request.style
        )
        
        logger.info(f"Summarization completed. Summary length: {len(result['summary'])}")
        
        return SummaryResponse(
            summary=result["summary"],
            word_count=result.get("word_count", 0),
            original_length=len(request.text),
            style=request.style,
            model_used=result.get("model_used", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.get("/summarize/status")
async def summarization_status():
    """
    Get the status of the summarization service.
    
    Returns:
        dict: Service status information
    """
    try:
        status = await llm_service.get_status()
        return {
            "status": "operational",
            "provider": status.get("provider", "unknown"),
            "model": status.get("model", "unknown"),
            "available": status.get("available", True)
        }
    except Exception as e:
        logger.error(f"Error getting summarization status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/summarize/batch")
async def summarize_batch_texts(request: list[SummaryRequest]):
    """
    Summarize multiple texts in batch.
    
    Args:
        request: List of SummaryRequest objects
        
    Returns:
        List of SummaryResponse objects
    """
    try:
        if not request or len(request) == 0:
            raise HTTPException(status_code=400, detail="No texts provided for batch summarization")
        
        if len(request) > 10:
            raise HTTPException(status_code=400, detail="Too many texts for batch processing (max 10)")
        
        logger.info(f"Processing batch summarization for {len(request)} texts")
        
        results = []
        for i, req in enumerate(request):
            try:
                result = await llm_service.summarize(
                    text=req.text,
                    max_length=req.max_length,
                    style=req.style
                )
                
                results.append(SummaryResponse(
                    summary=result["summary"],
                    word_count=result.get("word_count", 0),
                    original_length=len(req.text),
                    style=req.style,
                    model_used=result.get("model_used", "unknown")
                ))
                
            except Exception as e:
                logger.error(f"Error processing text {i}: {str(e)}")
                results.append(SummaryResponse(
                    summary=f"Error: {str(e)}",
                    word_count=0,
                    original_length=len(req.text),
                    style=req.style,
                    model_used="error"
                ))
        
        logger.info(f"Batch summarization completed for {len(results)} texts")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch summarization failed: {str(e)}") 