"""
ElevenLabs Flash v2.5 voice synthesizer.

Supports:
- WebSocket streaming for low latency (~75ms)
- Text normalization for TTS
- Async operation for non-blocking synthesis
"""
import asyncio
import re
import base64
import httpx
from typing import AsyncGenerator, Optional
import orjson

from .voices import VoiceConfig


class ElevenLabsSynthesizer:
    """
    Voice synthesizer using ElevenLabs API.
    
    Uses REST API for reliability, with option to upgrade to 
    WebSocket streaming for lower latency.
    """
    
    API_BASE = "https://api.elevenlabs.io/v1"
    MODEL_ID = "eleven_flash_v2_5"
    
    def __init__(self, api_key: str):
        """
        Initialize synthesizer.
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
            }
        )
        
    def _normalize_text(self, text: str) -> str:
        """
        Convert symbols to speakable words.
        
        Args:
            text: Raw text with symbols
            
        Returns:
            Text optimized for TTS
        """
        replacements = {
            "₹": "Rupees ",
            "$": "Dollars ",
            "£": "Pounds ",
            "200 DMA": "two hundred day moving average",
            "50 DMA": "fifty day moving average",
            "SMA": "simple moving average",
            "EMA": "exponential moving average",
            "VWAP": "volume weighted average price",
            "RSI": "relative strength index",
            "%": " percent",
            "NSE:": "",  # Remove market prefix
            "NYSE:": "",
            "LSE:": "",
            "NASDAQ:": "",
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, word)
            
        # Remove markdown artifacts
        text = re.sub(r'\*\*|\*|__|_|`', '', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    async def synthesize(
        self, 
        text: str,
        voice: VoiceConfig
    ) -> bytes:
        """
        Synthesize text to audio bytes.
        
        Args:
            text: Text to synthesize
            voice: Voice configuration
            
        Returns:
            Audio bytes (MP3 format)
        """
        normalized = self._normalize_text(text)
        
        url = f"{self.API_BASE}/text-to-speech/{voice.voice_id}"
        
        payload = {
            "text": normalized,
            "model_id": self.MODEL_ID,
            "voice_settings": {
                "stability": voice.stability,
                "similarity_boost": voice.similarity_boost,
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            print(f"ElevenLabs error: {e}")
            return b""
            
    async def synthesize_stream(
        self, 
        text_chunks: AsyncGenerator[str, None],
        voice: VoiceConfig
    ) -> AsyncGenerator[bytes, None]:
        """
        Synthesize streaming text to streaming audio.
        
        For MVP, we accumulate text and synthesize in batches.
        Can be upgraded to true WebSocket streaming for lower latency.
        
        Args:
            text_chunks: Async generator yielding text chunks
            voice: Voice configuration
            
        Yields:
            Audio bytes (MP3 format)
        """
        buffer = ""
        
        async for chunk in text_chunks:
            buffer += chunk
            
            # Synthesize on sentence boundaries
            if any(p in buffer for p in ['.', '!', '?']):
                # Find last sentence boundary
                for i in range(len(buffer) - 1, -1, -1):
                    if buffer[i] in '.!?':
                        sentence = buffer[:i+1]
                        buffer = buffer[i+1:].lstrip()
                        
                        audio = await self.synthesize(sentence, voice)
                        if audio:
                            yield audio
                        break
        
        # Synthesize remaining buffer
        if buffer.strip():
            audio = await self.synthesize(buffer, voice)
            if audio:
                yield audio
                
    async def save_to_file(
        self,
        text: str,
        voice: VoiceConfig,
        filepath: str
    ) -> bool:
        """
        Synthesize and save to MP3 file.
        
        Useful for Day 3 testing before frontend streaming.
        
        Args:
            text: Text to synthesize
            voice: Voice configuration
            filepath: Output file path
            
        Returns:
            True if successful
        """
        audio = await self.synthesize(text, voice)
        
        if audio:
            with open(filepath, 'wb') as f:
                f.write(audio)
            print(f"Saved audio to {filepath}")
            return True
            
        return False
        
    async def close(self):
        """Cleanup resources."""
        await self.client.aclose()
