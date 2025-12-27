"""
Tests for Technical Indicators: RSI and Volume Spike Detection.

Run with: pytest backend/tests/test_indicators.py -v
"""
import pytest
import time
from app.indicators.rsi import RSICalculator
from app.indicators.volume import VolumeSpikeDetector


class TestRSICalculator:
    """Test suite for RSICalculator."""
    
    def test_initialization(self):
        """Test RSI calculator initializes correctly."""
        rsi = RSICalculator(period=14)
        assert rsi.period == 14
        assert len(rsi.calculators) == 0
        
    def test_candle_formation(self):
        """Test that updates are aggregated into 1-second candles."""
        rsi = RSICalculator(period=14)
        symbol = "BTCUSDT"
        # Use a fixed timestamp at the start of a second (e.g., 1000000000000 ms)
        now = 1000000000000
        
        # Multiple updates in same second should update current candle
        rsi.update(symbol, 50000.0, now)
        rsi.update(symbol, 50100.0, now + 100)
        result = rsi.update(symbol, 50200.0, now + 500)
        
        # Should return None until candle is closed (by a new second)
        assert result is None
        
        # New second update should close previous candle
        next_sec = now + 1000
        result = rsi.update(symbol, 50300.0, next_sec)
        
        # Now we should have 2 candles in the deque:
        # 1. The closed candle from 'now' (50200.0)
        # 2. The open candle for 'next_sec' (50300.0)
        calc = rsi.calculators[symbol]
        assert len(calc.closes) == 2
        assert calc.closes[0] == 50200.0
        assert calc.closes[1] == 50300.0

    def test_rsi_calculation(self):
        """Test RSI calculation logic."""
        # Use small period for testing
        rsi = RSICalculator(period=2)
        symbol = "ETHUSDT"
        now = 1000000000000
        
        # Feed prices that go up -> RSI should be 100
        prices = [100.0, 110.0, 120.0, 130.0, 140.0] 
        
        last_result = None
        for i, price in enumerate(prices):
            # Advance time by 1.1s for each price to force candle closure
            t = now + (i * 1100)
            result = rsi.update(symbol, price, t)
            if result:
                last_result = result
                
        # With period 2, we need enough history for the calculation
        assert last_result is not None
        assert last_result.rsi > 90  # Should be high (overbought)
        assert last_result.is_overbought is True

    def test_rsi_down_trend(self):
        """Test RSI dropping."""
        rsi = RSICalculator(period=2)
        symbol = "SOLUSDT"
        now = 1000000000000
        
        prices = [100.0, 90.0, 80.0, 70.0, 60.0]
        
        last_result = None
        for i, price in enumerate(prices):
            t = now + (i * 1100)
            result = rsi.update(symbol, price, t)
            if result:
                last_result = result
                
        assert last_result is not None
        assert last_result.rsi < 10  # Should be low (oversold)
        assert last_result.is_oversold is True


class TestVolumeSpikeDetector:
    """Test suite for VolumeSpikeDetector."""
    
    def test_spike_detection(self):
        """Test volume spike logic."""
        detector = VolumeSpikeDetector(window_size=10)
        symbol = "BTCUSDT"
        now = 1000000000000
        
        # Feed normal volume for 15 seconds
        for i in range(15):
            t = now + (i * 1000)
            # Add tick, then add another tick in next second to close it
            detector.update(symbol, 1.0, t)
            
        # Feed massive volume spike at t + 15s
        spike_time = now + (15 * 1000)
        detector.update(symbol, 10.0, spike_time)
        
        # To detect the spike, we need to complete the window holding the 10.0 volume
        # So we send a tick at t + 16s
        check_time = now + (16 * 1000)
        result = detector.update(symbol, 1.0, check_time)
        
        # Now 'result' corresponds to the completed window from spike_time (volume 10.0)
        assert result is not None
        assert result.is_spike is True
        assert result.spike_multiplier >= 5.0

