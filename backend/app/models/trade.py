"""
Trade event models for crypto streaming.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import orjson


class TradeEvent(BaseModel):
    """
    Normalized trade event from Binance WebSocket.
    
    Binance raw format:
    {
        "e": "trade",
        "s": "BTCUSDT",
        "p": "67540.50",
        "q": "0.001",
        "T": 1703683200000
    }
    """
    symbol: str        # BTCUSDT, ETHUSDT, SOLUSDT
    price: float       # Trade price
    volume: float      # Trade quantity
    time: int          # Unix timestamp (ms)
    
    @classmethod
    def from_binance(cls, data: dict) -> "TradeEvent":
        """Parse Binance trade stream message."""
        return cls(
            symbol=data['s'],
            price=float(data['p']),
            volume=float(data['q']),
            time=data['T']
        )
    
    def to_kafka_bytes(self) -> bytes:
        """Serialize for Kafka (faster than JSON)."""
        return orjson.dumps({
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "time": self.time
        })
    
    @classmethod
    def from_kafka_bytes(cls, data: bytes) -> "TradeEvent":
        """Deserialize from Kafka."""
        parsed = orjson.loads(data)
        return cls(**parsed)
    
    @property
    def timestamp(self) -> datetime:
        """Convert Unix ms to datetime."""
        return datetime.fromtimestamp(self.time / 1000)


class AlertEvent(BaseModel):
    """
    Alert triggered by technical analysis.
    """
    symbol: str
    price: float
    trigger_type: str   # RSI_HIGH, RSI_LOW, VOLUME_SPIKE, PRICE_LEVEL
    trigger_value: float
    message: str
    time: int
    
    def to_kafka_bytes(self) -> bytes:
        """Serialize for Kafka."""
        return orjson.dumps(self.model_dump())
    
    @classmethod
    def from_kafka_bytes(cls, data: bytes) -> "AlertEvent":
        """Deserialize from Kafka."""
        return cls(**orjson.loads(data))
