"""
Gemini 2.5 Flash integration for real-time market analysis.

Uses the new google-genai SDK (replaces deprecated google-generativeai).
"""
from google import genai
from google.genai import types
from typing import AsyncGenerator
import asyncio

from .prompts import PULSETRADE_SYSTEM_PROMPT


class GeminiLiveClient:
    """
    Client for Gemini 2.5 Flash API.
    
    Provides:
    - System prompt configuration (Victor Sterling persona)
    - Streaming text generation
    - Async support for non-blocking operation
    """
    
    MODEL_NAME = "gemini-2.5-flash"  # Gemini 2.5 Flash
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        self.client = None
        
    async def connect(self):
        """Initialize the Gemini client."""
        self.client = genai.Client(api_key=self.api_key)
        print(f"Gemini {self.MODEL_NAME} initialized (new SDK)")
        
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from Gemini.
        
        Args:
            prompt: The market alert prompt
            
        Yields:
            Text chunks as they are generated
        """
        if not self.client:
            await self.connect()
            
        try:
            response = self.client.models.generate_content_stream(
                model=self.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=PULSETRADE_SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=256,
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                await asyncio.sleep(0)
                
        except Exception as e:
            print(f"Gemini error: {e}")
            yield f"Analysis unavailable: {str(e)}"
            
    async def generate(self, prompt: str) -> str:
        """
        Generate complete response (non-streaming).
        
        Args:
            prompt: The market alert prompt
            
        Returns:
            Complete text response
        """
        if not self.client:
            await self.connect()
            
        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=PULSETRADE_SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=256,
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            return f"Analysis unavailable: {str(e)}"
            
    async def close(self):
        """Cleanup resources."""
        pass
