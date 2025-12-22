"""
Voice configurations for different markets.

Each market has a distinct voice persona:
- India (NSE): Energetic, fast-paced
- UK (LSE): Authoritative, BBC-style
- US (NYSE/NASDAQ): Broadcast professional, CNBC-style
"""
import os
from dataclasses import dataclass
from typing import Dict

from app.models.tick import Market


@dataclass
class VoiceConfig:
    """Configuration for a specific voice."""
    voice_id: str
    name: str
    style: str
    stability: float = 0.5
    similarity_boost: float = 0.75
    

def get_market_voices() -> Dict[Market, VoiceConfig]:
    """
    Get voice configurations for each market.
    
    Voice IDs are loaded from environment variables.
    To discover voice IDs, run:
        curl -X GET "https://api.elevenlabs.io/v1/voices" \
             -H "xi-api-key: YOUR_API_KEY"
    
    Returns:
        Dict mapping Market to VoiceConfig
    """
    return {
        Market.NSE: VoiceConfig(
            voice_id=os.getenv("VOICE_ID_INDIA", "21m00Tcm4TlvDq8ikWAM"),
            name="Ayesha",
            style="Energetic, Fast-Paced, Clear Indian English"
        ),
        Market.LSE: VoiceConfig(
            voice_id=os.getenv("VOICE_ID_UK", "pNInz6obpgDQGcFmaJgB"),
            name="Russell",
            style="Deep, Authoritative, BBC News Style"
        ),
        Market.NYSE: VoiceConfig(
            voice_id=os.getenv("VOICE_ID_US", "ErXwobaYiN019PkySvjV"),
            name="Prime Time Anchor",
            style="Broadcast Professional, CNBC Style"
        ),
        Market.NASDAQ: VoiceConfig(
            voice_id=os.getenv("VOICE_ID_US", "ErXwobaYiN019PkySvjV"),
            name="Prime Time Anchor",
            style="Broadcast Professional, CNBC Style"
        ),
    }
