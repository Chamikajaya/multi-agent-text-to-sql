"""
LLM Utilities

Handles initialization and configuration of the language model.
Uses a singleton pattern to ensure only one LLM instance is created.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

from src.config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
    LLM_MAX_RETRIES,
    get_google_api_key
)


# Global LLM instance (singleton pattern)
_llm_instance: Optional[ChatGoogleGenerativeAI] = None


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Get or create the LLM instance.
    
    Uses a singleton pattern to ensure only one LLM instance is created
    throughout the application lifecycle, reducing initialization overhead.
    
    Returns:
        ChatGoogleGenerativeAI: Configured language model instance
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set
    """
    global _llm_instance
    
    # Return existing instance if available
    if _llm_instance is not None:
        return _llm_instance
    
    # Ensure API key is set
    api_key = get_google_api_key()
    
    # Create new LLM instance
    _llm_instance = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT,
        max_retries=LLM_MAX_RETRIES,
    )
    
    return _llm_instance


def reset_llm() -> None:
    """
    Reset the LLM instance.
    
    Useful for testing or when configuration changes require a new instance.
    """
    global _llm_instance
    _llm_instance = None
