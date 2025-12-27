"""
ElevenLabs Voice Synthesis Service.

Converts AI analysis text to speech using ElevenLabs.
"""
import re
from typing import Callable, Awaitable
from ddtrace import tracer
from elevenlabs.client import ElevenLabs

from app.core.config import get_settings


class VoiceService:
    """
    Voice synthesis using ElevenLabs.
    """
    
    def __init__(self):
        settings = get_settings()
        self.client = ElevenLabs(api_key=settings.eleven_api_key)
        self.voice_id = settings.eleven_voice_id
        self.model = "eleven_turbo_v2_5"
        
        print(f"[Voice] Initialized with voice_id={self.voice_id}, api_key={settings.eleven_api_key[:10]}...")
        
        # Callback for streaming audio chunks
        self.on_audio_chunk: Callable[[bytes], Awaitable[None]] | None = None
        
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for TTS.
        
        Converts symbols and abbreviations to speakable words.
        """
        replacements = {
            "$": "dollars ",
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "SOL": "Solana",
            "USDT": "US D T",
            "RSI": "R S I",
            "%": " percent",
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, word)
            
        # Remove markdown artifacts
        text = re.sub(r'\*\*|__|`', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio bytes.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes (MP3)
        """
        normalized = self._normalize_text(text)
        
        with tracer.trace("elevenlabs.synthesize", service="pulsetrade-voice") as span:
            span.set_tag("text_length", len(normalized))
            
            try:
                # Use text_to_speech API (v2)
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=self.voice_id,
                    text=normalized,
                    model_id=self.model,
                )
                
                # Collect all chunks - REVERTED to buffering for stability
                audio_bytes = b"".join(audio_generator)
                span.set_tag("audio_size", len(audio_bytes))
                
                print(f"[Voice] Generated {len(audio_bytes)} bytes of audio")
                return audio_bytes
                
            except Exception as e:
                print(f"[Voice] ElevenLabs error: {e}")
                return b""
                
    async def speak(self, text: str):
        """
        Synthesize and broadcast audio via callback.
        
        This is the main method to call from the analyzer.
        """
        print(f"[Voice] Speaking: {text[:50]}...")
        
        audio = await self.synthesize(text)
        
        if audio:
            print(f"[Voice] Broadcasting {len(audio)} bytes to WebSocket")
            if self.on_audio_chunk:
                await self.on_audio_chunk(audio)
        else:
            print("[Voice] No audio generated")
            
        return audio


# Singleton
_voice_service: VoiceService | None = None


def get_voice_service() -> VoiceService:
    """Get singleton voice service."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
