"""
Pydantic Settings for application configuration.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Kafka / Confluent
    kafka_bootstrap_servers: str = ""
    kafka_api_key: str = ""
    kafka_api_secret: str = ""
    
    # Google AI
    google_api_key: str = ""
    
    # ElevenLabs
    eleven_api_key: str = ""
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
