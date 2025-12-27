"""
RSI (Relative Strength Index) Calculator.

Uses sliding window for real-time calculation.
"""
from collections import deque
from dataclasses import dataclass
from typing import Dict


@dataclass
class RSIResult:
    """RSI calculation result."""
    symbol: str
    rsi: float
    is_overbought: bool  # RSI > 80
    is_oversold: bool    # RSI < 20


class RSICalculator:
    """
    Sliding window RSI calculator.
    
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss over N periods
    """
    
    def __init__(self, period: int = 14):
        """
        Initialize calculator.
        
        Args:
            period: Number of periods for RSI calculation
        """
        self.period = period
        self.prices: Dict[str, deque] = {}
        self.gains: Dict[str, deque] = {}
        self.losses: Dict[str, deque] = {}
        
    def update(self, symbol: str, price: float) -> RSIResult | None:
        """
        Update RSI with new price.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            
        Returns:
            RSIResult if enough data, None otherwise
        """
        # Initialize deques for new symbols
        if symbol not in self.prices:
            self.prices[symbol] = deque(maxlen=self.period + 1)
            self.gains[symbol] = deque(maxlen=self.period)
            self.losses[symbol] = deque(maxlen=self.period)
            
        prices = self.prices[symbol]
        gains = self.gains[symbol]
        losses = self.losses[symbol]
        
        # Calculate change
        if prices:
            change = price - prices[-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
                
        prices.append(price)
        
        # Need at least 'period' data points
        if len(gains) < self.period:
            return None
            
        # Calculate RSI
        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
        return RSIResult(
            symbol=symbol,
            rsi=round(rsi, 2),
            is_overbought=rsi > 80,
            is_oversold=rsi < 20,
        )
    
    def get_rsi(self, symbol: str) -> float | None:
        """Get current RSI for a symbol."""
        if symbol not in self.gains or len(self.gains[symbol]) < self.period:
            return None
            
        gains = self.gains[symbol]
        losses = self.losses[symbol]
        
        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
