"""
LLM service for text summarization
Supports both OpenAI GPT and Hugging Face models
"""

import os
import logging
import re
from typing import Dict, Any, Optional
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for handling text summarization using LLM models"""
    
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.huggingface_model = os.getenv("HUGGINGFACE_MODEL", "facebook/bart-large-cnn")
        
        # Initialize models based on provider
        self.summarizer = None
        self.tokenizer = None
        self.model = None
        
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                raise Exception("OpenAI API key required when using OpenAI provider")
            openai.api_key = self.openai_api_key
            logger.info(f"OpenAI LLM configured with model: {self.openai_model}")
            
        elif self.llm_provider == "huggingface":
            try:
                logger.info(f"Loading Hugging Face model: {self.huggingface_model}")
                self.summarizer = pipeline("summarization", model=self.huggingface_model)
                logger.info("Hugging Face model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Hugging Face model: {str(e)}")
                raise Exception(f"Failed to initialize Hugging Face model: {str(e)}")
        
        else:
            raise Exception(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def summarize(self, text: str, max_length: int = 150, style: str = "bullet_points") -> Dict[str, Any]:
        """
        Summarize text using the configured LLM provider.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            style: Summary style (bullet_points, paragraph, executive, technical)
            
        Returns:
            Dict containing summary, word count, and model information
        """
        try:
            if self.llm_provider == "openai":
                return await self._summarize_with_openai(text, max_length, style)
            elif self.llm_provider == "huggingface":
                return await self._summarize_with_huggingface(text, max_length, style)
            else:
                raise Exception(f"Unsupported LLM provider: {self.llm_provider}")
                
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            raise Exception(f"Summarization failed: {str(e)}")
    
    async def _summarize_with_openai(self, text: str, max_length: int, style: str) -> Dict[str, Any]:
        """Summarize using OpenAI GPT models"""
        try:
            logger.info(f"Using OpenAI {self.openai_model} for summarization")
            
            # Create prompt based on style
            prompt = self._create_openai_prompt(text, style)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in creating clear and concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length * 2,  # Approximate token count
                temperature=0.3,
                top_p=0.9
            )
            
            summary = response.choices[0].message.content.strip()
            word_count = len(summary.split())
            
            logger.info(f"OpenAI summarization completed. Word count: {word_count}")
            
            return {
                "summary": summary,
                "word_count": word_count,
                "model_used": self.openai_model,
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI summarization failed: {str(e)}")
            raise Exception(f"OpenAI summarization failed: {str(e)}")
    
    async def _summarize_with_huggingface(self, text: str, max_length: int, style: str) -> Dict[str, Any]:
        """Summarize using Hugging Face models"""
        try:
            logger.info(f"Using Hugging Face model for summarization")
            
            # Prepare text for summarization
            # Split long text into chunks if necessary
            max_chunk_length = 1024  # Maximum tokens for BART
            chunks = self._split_text_into_chunks(text, max_chunk_length)
            
            summaries = []
            for chunk in chunks:
                # Generate summary for each chunk
                result = self.summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=30,
                    do_sample=False,
                    truncation=True
                )
                summaries.append(result[0]['summary_text'])
            
            # Combine summaries if multiple chunks
            if len(summaries) > 1:
                combined_summary = " ".join(summaries)
                # Re-summarize the combined summary if it's still too long
                if len(combined_summary.split()) > max_length:
                    result = self.summarizer(
                        combined_summary,
                        max_length=max_length,
                        min_length=30,
                        do_sample=False,
                        truncation=True
                    )
                    final_summary = result[0]['summary_text']
                else:
                    final_summary = combined_summary
            else:
                final_summary = summaries[0]
            
            # Apply style formatting
            formatted_summary = self._apply_style_formatting(final_summary, style)
            word_count = len(formatted_summary.split())
            
            logger.info(f"Hugging Face summarization completed. Word count: {word_count}")
            
            return {
                "summary": formatted_summary,
                "word_count": word_count,
                "model_used": self.huggingface_model,
                "provider": "huggingface"
            }
            
        except Exception as e:
            logger.error(f"Hugging Face summarization failed: {str(e)}")
            raise Exception(f"Hugging Face summarization failed: {str(e)}")
    
    def _create_openai_prompt(self, text: str, style: str) -> str:
        """Create appropriate prompt for OpenAI based on style"""
        base_prompt = f"Please summarize the following text clearly and concisely. "
        
        if style == "bullet_points":
            base_prompt += "Use bullet points to highlight key information and action items. "
        elif style == "paragraph":
            base_prompt += "Provide a coherent paragraph summary. "
        elif style == "executive":
            base_prompt += "Create an executive summary suitable for business presentations. "
        elif style == "technical":
            base_prompt += "Provide a technical summary with specific details and terminology. "
        
        base_prompt += f"Keep the summary under {150} words. Here's the text to summarize:\n\n{text}"
        
        return base_prompt
    
    def _split_text_into_chunks(self, text: str, max_length: int) -> list[str]:
        """Split long text into chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _apply_style_formatting(self, summary: str, style: str) -> str:
        """Apply style formatting to the summary"""
        if style == "bullet_points":
            # Convert sentences to bullet points
            sentences = re.split(r'[.!?]+', summary)
            bullet_points = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Only meaningful sentences
                    bullet_points.append(f"• {sentence}")
            return "\n".join(bullet_points)
        
        elif style == "executive":
            # Add executive summary formatting
            return f"EXECUTIVE SUMMARY:\n\n{summary}"
        
        elif style == "technical":
            # Add technical summary formatting
            return f"TECHNICAL SUMMARY:\n\n{summary}"
        
        else:
            # Default paragraph style
            return summary
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the LLM service"""
        try:
            if self.llm_provider == "openai":
                return {
                    "provider": "openai",
                    "model": self.openai_model,
                    "available": True,
                    "api_key_configured": bool(self.openai_api_key)
                }
            elif self.llm_provider == "huggingface":
                return {
                    "provider": "huggingface",
                    "model": self.huggingface_model,
                    "available": self.summarizer is not None,
                    "model_loaded": self.summarizer is not None
                }
            else:
                return {
                    "provider": "unknown",
                    "model": "unknown",
                    "available": False,
                    "error": f"Unsupported provider: {self.llm_provider}"
                }
        except Exception as e:
            logger.error(f"Error getting LLM status: {str(e)}")
            return {
                "provider": "unknown",
                "model": "unknown",
                "available": False,
                "error": str(e)
            } 