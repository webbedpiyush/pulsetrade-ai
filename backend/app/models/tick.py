"""Canonical tick data model with Decimal precision for financial math."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class MarketStatus(Enum):
    """Market trading status."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    HALTED = "HALTED"


class Market(Enum):
    """Supported market exchanges."""
    NSE = "NSE"
    LSE = "LSE"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"


@dataclass
class NormalizedTick:
    """
    Canonical tick format for all markets.
    Uses Decimal for price to avoid floating-point precision issues.
    """
    symbol: str                        # e.g., "NSE:INFY", "NYSE:AAPL"
    price: Decimal                     # Use Decimal for financial math
    volume: int
    timestamp: int                     # Unix epoch (UTC) milliseconds
    market: Market
    market_status: MarketStatus
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    liquidity_score: Optional[float] = None
    raw_currency: str = "USD"
    
    def price_float(self) -> float:
        """Convert price to float for numpy/chart operations."""
        return float(self.price)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict (floats, not Decimals)."""
        return {
            "symbol": self.symbol,
            "price": float(self.price),
            "volume": self.volume,
            "timestamp": self.timestamp,
            "market": self.market.value,
            "market_status": self.market_status.value,
            "bid": float(self.bid) if self.bid else None,
            "ask": float(self.ask) if self.ask else None,
            "liquidity_score": self.liquidity_score,
            "raw_currency": self.raw_currency,
        }
