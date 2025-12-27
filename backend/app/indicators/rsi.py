"""
RSI (Relative Strength Index) Calculator.

Uses 1-second candle aggregation for meaningful real-time calculation.
This prevents high-frequency tick noise from causing extreme RSI values.
"""
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RSIResult:
    """RSI calculation result."""
    symbol: str
    rsi: float
    is_overbought: bool  # RSI > 70 (adjusted for 60-second period)
    is_oversold: bool    # RSI < 30 (adjusted for 60-second period)


class TimeBasedRSI:
    """
    Time-windowed RSI calculator using 1-second candles.
    
    Instead of calculating RSI on every tick (which creates noise),
    we aggregate ticks into 1-second buckets and calculate RSI
    on the close price of each second.
    
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss over N periods (seconds)
    """
    
    def __init__(self, period: int = 14):
        """
        Initialize calculator.
        
        Args:
            period: Number of 1-second candles for RSI calculation
        """
        self.period = period
        # Store close prices for each 1-second candle
        self.closes: deque = deque(maxlen=period + 1)
        self.last_candle_time: int = 0
        self.current_price: float = 0.0
        
    def add_tick(self, price: float, timestamp_ms: int) -> Optional[float]:
        """
        Process a tick and return RSI if a new second has completed.
        
        Args:
            price: Current trade price
            timestamp_ms: Trade timestamp in milliseconds
            
        Returns:
            RSI value if a new 1-second candle completed, None otherwise
        """
        # Convert ms to seconds (truncate to bucket by second)
        current_second = timestamp_ms // 1000
        self.current_price = price
        
        # First tick ever
        if self.last_candle_time == 0:
            self.last_candle_time = current_second
            self.closes.append(price)
            return None
        
        # New second? Complete the previous candle
        if current_second > self.last_candle_time:
            # The previous close is already in the deque
            # Now add the new candle's opening price
            self.closes.append(price)
            self.last_candle_time = current_second
            
            # Calculate RSI if we have enough candles
            if len(self.closes) > self.period:
                return self._calculate_rsi()
        else:
            # Same second - update the current candle's close price
            if len(self.closes) > 0:
                self.closes[-1] = price
                
        return None
    
    def _calculate_rsi(self) -> float:
        """Calculate RSI from the stored close prices."""
        if len(self.closes) < 2:
            return 50.0  # Neutral
            
        closes = list(self.closes)
        
        # Calculate price changes
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))
        
        # Use only the last 'period' changes
        gains = gains[-self.period:]
        losses = losses[-self.period:]
        
        avg_gain = sum(gains) / len(gains) if gains else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        
        # Handle edge cases
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        if avg_gain == 0:
            return 0.0
            
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return round(rsi, 2)


class RSICalculator:
    """
    Multi-symbol RSI calculator using time-based sampling.
    
    Maintains separate TimeBasedRSI instances for each symbol.
    """
    
    def __init__(self, period: int = 14):
        """
        Initialize calculator.
        
        Args:
            period: Number of 1-second periods for RSI calculation
        """
        self.period = period
        self.calculators: Dict[str, TimeBasedRSI] = {}
        
    def update(self, symbol: str, price: float, timestamp_ms: int = None) -> RSIResult | None:
        """
        Update RSI with new price tick.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            timestamp_ms: Trade timestamp in milliseconds (uses current time if None)
            
        Returns:
            RSIResult if a 1-second candle completed, None otherwise
        """
        import time
        
        if timestamp_ms is None:
            timestamp_ms = int(time.time() * 1000)
            
        # Initialize calculator for new symbols
        if symbol not in self.calculators:
            self.calculators[symbol] = TimeBasedRSI(period=self.period)
            
        # Add tick and check if we got a new RSI value
        rsi = self.calculators[symbol].add_tick(price, timestamp_ms)
        
        if rsi is not None:
            return RSIResult(
                symbol=symbol,
                rsi=rsi,
                is_overbought=rsi > 70,  # Adjusted for 60-second RSI
                is_oversold=rsi < 30,    # Adjusted for 60-second RSI
            )
            
        return None
    
    def get_rsi(self, symbol: str) -> float | None:
        """Get current RSI for a symbol."""
        if symbol not in self.calculators:
            return None
            
        calc = self.calculators[symbol]
        if len(calc.closes) <= calc.period:
            return None
            
        return calc._calculate_rsi()
