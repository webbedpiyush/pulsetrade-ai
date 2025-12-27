"""
Price-based Indicators: Whale Alerts and Psychological Levels.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import time


@dataclass
class PriceChangeResult:
    """Result of a price change check."""
    symbol: str
    change_percent: float  # Percentage change (e.g., 1.2 for 1.2%)
    time_window_sec: int   # Window size in seconds
    is_whale_move: bool    # True if abs(change) > threshold


class PriceChangeDetector:
    """
    Detects significant price movements (Whale Alerts) over a time window.
    
    Tracks the open price of rolling time windows.
    Since we need to detect "Price moved > 1% in LAST 1 minute", we need
    to compare current price with price 60 seconds ago.
    
    Implementation:
    - Store a circular buffer or list of (timestamp, price) tuples.
    - On update, clean up old history (> window size).
    - Compare current price with the oldest price in the window.
    """
    
    def __init__(self, window_seconds: int = 60, threshold_percent: float = 1.0):
        self.window_seconds = window_seconds
        self.threshold_percent = threshold_percent
        # {symbol: [(ts, price), ...]}
        self.history: Dict[str, List[tuple[int, float]]] = {}
        
    def update(self, symbol: str, price: float, timestamp_ms: int) -> Optional[PriceChangeResult]:
        """
        Update price and check for significant change.
        """
        if symbol not in self.history:
            self.history[symbol] = []
            
        history = self.history[symbol]
        
        # Add new point
        history.append((timestamp_ms, price))
        
        # Remove points older than window
        cutoff = timestamp_ms - (self.window_seconds * 1000)
        
        # Optimize: remove from front while too old
        while history and history[0][0] < cutoff:
            history.pop(0)
            
        if not history:
            return None
            
        # Compare current price with oldest valid price in window
        oldest_price = history[0][1]
        
        change_pct = ((price - oldest_price) / oldest_price) * 100.0
        
        if abs(change_pct) >= self.threshold_percent:
            return PriceChangeResult(
                symbol=symbol,
                change_percent=round(change_pct, 2),
                time_window_sec=self.window_seconds,
                is_whale_move=True
            )
            
        return None


@dataclass
class LevelResult:
    """Result of a level crossing check."""
    symbol: str
    level: int
    direction: str  # "UP" or "DOWN"
    price: float


class LevelCrossDetector:
    """
    Detects when price crosses specific psychological/integer levels.
    """
    
    def __init__(self, levels: List[int]):
        self.levels = sorted(levels)
        # {symbol: last_price}
        self.last_prices: Dict[str, float] = {}
        
    def update(self, symbol: str, price: float) -> Optional[LevelResult]:
        """
        Check if price crossed any level since last update.
        """
        if symbol not in self.last_prices:
            self.last_prices[symbol] = price
            return None
            
        last_price = self.last_prices[symbol]
        self.last_prices[symbol] = price
        
        # Check crossings
        for level in self.levels:
            # Crossed UP
            if last_price < level <= price:
                return LevelResult(symbol, level, "UP", price)
            
            # Crossed DOWN
            if last_price > level >= price:
                return LevelResult(symbol, level, "DOWN", price)
                
        return None
