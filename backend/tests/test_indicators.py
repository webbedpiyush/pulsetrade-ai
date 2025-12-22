"""
Tests for the IndicatorEngine.
Validates SMA, volatility, and breakout detection.

Run with: pytest tests/test_indicators.py -v
"""
import pytest
from app.processors.indicators import IndicatorEngine, TechnicalSnapshot


class TestIndicatorEngine:
    """Test suite for IndicatorEngine."""
    
    def test_initialization(self):
        """Test engine initializes with empty windows."""
        engine = IndicatorEngine()
        assert engine.get_symbol_count() == 0
        
    def test_single_tick(self):
        """Test processing a single tick."""
        engine = IndicatorEngine()
        snapshot = engine.update("NSE:INFY", 1500.0, 10000)
        
        assert snapshot.symbol == "NSE:INFY"
        assert snapshot.sma_5 == 1500.0
        assert snapshot.vwap == 1500.0
        assert snapshot.volatility == 0.0
        assert snapshot.is_breakout is False
        
    def test_multiple_ticks_same_symbol(self):
        """Test SMA calculation with multiple ticks."""
        engine = IndicatorEngine()
        
        # Add 35 ticks at price 100
        for _ in range(35):
            engine.update("NSE:TCS", 100.0, 1000)
            
        # SMA(30) should be close to 100
        snapshot = engine.update("NSE:TCS", 100.0, 1000)
        assert 99.0 <= snapshot.sma_5 <= 101.0
        
    def test_breakout_detection_up(self):
        """Test breakout detection for upward move."""
        engine = IndicatorEngine()
        
        # Establish baseline at 100
        for _ in range(50):
            engine.update("NSE:RELIANCE", 100.0, 1000)
            
        # Spike to 120 (20% jump, should trigger breakout)
        snapshot = engine.update("NSE:RELIANCE", 120.0, 2000)
        
        # With consistent prices, volatility is near 0
        # A 20% jump should exceed 2 * volatility
        assert snapshot.is_breakout is True
        assert snapshot.breakout_direction == "UP"
        
    def test_breakout_detection_down(self):
        """Test breakout detection for downward move."""
        engine = IndicatorEngine()
        
        # Establish baseline at 100
        for _ in range(50):
            engine.update("NSE:HDFC", 100.0, 1000)
            
        # Drop to 80 (20% drop, should trigger breakout)
        snapshot = engine.update("NSE:HDFC", 80.0, 2000)
        
        assert snapshot.is_breakout is True
        assert snapshot.breakout_direction == "DOWN"
        
    def test_no_breakout_normal_volatility(self):
        """Test no false breakouts during normal volatility."""
        engine = IndicatorEngine()
        
        # Add prices with some natural variance
        import random
        for _ in range(50):
            price = 100.0 + random.uniform(-1, 1)  # ±1% variance
            engine.update("NSE:ICICI", price, 1000)
            
        # Small move within normal range
        snapshot = engine.update("NSE:ICICI", 100.5, 1000)
        
        # Should not trigger breakout for small moves
        assert snapshot.is_breakout is False
        
    def test_multiple_symbols(self):
        """Test tracking multiple symbols independently."""
        engine = IndicatorEngine()
        
        engine.update("NSE:INFY", 1500.0, 1000)
        engine.update("NSE:TCS", 3800.0, 2000)
        engine.update("NYSE:AAPL", 190.0, 5000)
        
        assert engine.get_symbol_count() == 3
        
    def test_vwap_calculation(self):
        """Test VWAP is volume-weighted."""
        engine = IndicatorEngine()
        
        # Low price, high volume
        engine.update("NSE:TEST", 100.0, 10000)
        # High price, low volume
        snapshot = engine.update("NSE:TEST", 200.0, 1000)
        
        # VWAP should be weighted toward 100 (higher volume)
        # VWAP = (100*10000 + 200*1000) / (10000 + 1000) = 109.09
        assert 108.0 <= snapshot.vwap <= 110.0
        
    def test_to_dict_serialization(self):
        """Test snapshot serializes to JSON-safe dict."""
        engine = IndicatorEngine()
        snapshot = engine.update("NSE:INFY", 1500.0, 10000)
        
        data = snapshot.to_dict()
        
        assert isinstance(data, dict)
        assert data["symbol"] == "NSE:INFY"
        assert isinstance(data["sma_5"], float)
        assert isinstance(data["is_breakout"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
