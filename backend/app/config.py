"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Kite Connect (India)
    KITE_API_KEY: str = ""
    KITE_ACCESS_TOKEN: str = ""
    
    # Finage (US/UK)
    FINAGE_API_KEY: str = ""
    
    # Gemini
    GEMINI_API_KEY: str = ""
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Voice IDs (ElevenLabs)
    VOICE_ID_INDIA: str = "21m00Tcm4TlvDq8ikWAM"
    VOICE_ID_UK: str = "pNInz6obpgDQGcFmaJgB"
    VOICE_ID_US: str = "ErXwobaYiN019PkySvjV"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
