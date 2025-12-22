"""
Technical indicator calculations using sliding windows.

Provides real-time SMA, volatility, VWAP, and breakout detection.
"""
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class TechnicalSnapshot:
    """Snapshot of technical indicators for a symbol."""
    symbol: str
    sma_5: float
    sma_20: float
    volatility: float
    vwap: float
    rsi: Optional[float]
    is_breakout: bool
    breakout_direction: str  # "UP", "DOWN", "NONE"
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "symbol": self.symbol,
            "sma_5": round(self.sma_5, 2),
            "sma_20": round(self.sma_20, 2),
            "volatility": round(self.volatility, 4),
            "vwap": round(self.vwap, 2),
            "rsi": round(self.rsi, 2) if self.rsi else None,
            "is_breakout": self.is_breakout,
            "breakout_direction": self.breakout_direction,
        }


class IndicatorEngine:
    """
    Real-time technical indicator calculator.
    
    Maintains sliding windows of price/volume data per symbol.
    Thread-safe for use in async workers.
    """
    
    def __init__(self, window_size: int = 300):
        """
        Initialize indicator engine.
        
        Args:
            window_size: Number of ticks to keep (5 min @ 1 tick/sec)
        """
        self.window_size = window_size
        self.price_windows: Dict[str, deque] = {}
        self.volume_windows: Dict[str, deque] = {}
        
    def update(self, symbol: str, price: float, volume: int) -> TechnicalSnapshot:
        """
        Update indicators with new tick.
        
        Args:
            symbol: Instrument symbol (e.g., "NSE:INFY")
            price: Current price (as float)
            volume: Current cumulative volume
            
        Returns:
            TechnicalSnapshot with current indicator values
        """
        # Initialize windows if new symbol
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
            self.volume_windows[symbol] = deque(maxlen=self.window_size)
            
        # Append new data
        self.price_windows[symbol].append(price)
        self.volume_windows[symbol].append(volume)
        
        # Convert to numpy for calculations
        prices = np.array(self.price_windows[symbol])
        volumes = np.array(self.volume_windows[symbol])
        
        # SMA calculations (30 ticks ~ 30 sec, 120 ticks ~ 2 min)
        sma_5 = float(np.mean(prices[-30:])) if len(prices) >= 30 else price
        sma_20 = float(np.mean(prices[-120:])) if len(prices) >= 120 else price
        
        # Volatility (standard deviation)
        volatility = float(np.std(prices)) if len(prices) > 1 else 0.0
        
        # VWAP (Volume Weighted Average Price)
        total_volume = np.sum(volumes)
        if total_volume > 0:
            vwap = float(np.sum(prices * volumes) / total_volume)
        else:
            vwap = price
        
        # Breakout detection: price deviates > 2 * volatility from SMA
        deviation = abs(price - sma_5)
        is_breakout = deviation > 2 * volatility if volatility > 0 else False
        
        # Determine direction
        if is_breakout:
            direction = "UP" if price > sma_5 else "DOWN"
        else:
            direction = "NONE"
        
        return TechnicalSnapshot(
            symbol=symbol,
            sma_5=sma_5,
            sma_20=sma_20,
            volatility=volatility,
            vwap=vwap,
            rsi=None,  # TODO: Implement RSI
            is_breakout=is_breakout,
            breakout_direction=direction,
        )
    
    def get_symbol_count(self) -> int:
        """Get number of tracked symbols."""
        return len(self.price_windows)
