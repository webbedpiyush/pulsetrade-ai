"""
Pydantic Settings for application configuration.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Kafka / Confluent
    kafka_bootstrap_servers: str = ""
    kafka_api_key: str = ""
    kafka_api_secret: str = ""
    
    # Google AI (supports both GOOGLE_API_KEY and GEMINI_API_KEY)
    google_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    
    # ElevenLabs (supports both ELEVEN_API_KEY and ELEVENLABS_API_KEY)
    eleven_api_key: str = Field(default="", alias="ELEVENLABS_API_KEY")
    eleven_voice_id: str = "Brian"
    
    # Datadog
    dd_api_key: str = ""
    dd_site: str = "datadoghq.com"
    dd_service: str = "pulsetrade-crypto"
    
    # App
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
