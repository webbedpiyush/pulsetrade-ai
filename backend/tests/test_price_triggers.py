"""
Tests for Price-based Indicators: Whale Alerts and Psychological Levels.

Run with: pytest backend/tests/test_price_triggers.py -v
"""
import pytest
from app.indicators.price import PriceChangeDetector, LevelCrossDetector


class TestPriceChangeDetector:
    """Test suite for Whale Alert detector."""
    
    def test_whale_alert_pump(self):
        """Test detection of >1% price pump within window."""
        # 1% threshold, 60s window
        detector = PriceChangeDetector(window_seconds=60, threshold_percent=1.0)
        symbol = "BTCUSDT"
        now = 1000000000  # ms
        
        # Initial price: 50,000
        detector.update(symbol, 50000.0, now)
        
        # 30s later: Price moves to 50,200 (+0.4%) -> No alert
        result = detector.update(symbol, 50200.0, now + 30000)
        assert result is None
        
        # 50s later: Price moves to 50,600 (+1.2% from 50,000) -> Alert!
        # (50600 - 50000) / 50000 = 600 / 50000 = 0.012 = 1.2%
        result = detector.update(symbol, 50600.0, now + 50000)
        
        assert result is not None
        assert result.is_whale_move is True
        assert result.change_percent == 1.2
        assert result.symbol == symbol

    def test_whale_alert_dump(self):
        """Test detection of >1% price dump."""
        detector = PriceChangeDetector(window_seconds=60, threshold_percent=1.0)
        symbol = "ETHUSDT"
        now = 1000000000
        
        # Initial: 3000
        detector.update(symbol, 3000.0, now)
        
        # Dump to 2900 (-3.33%) immediately
        result = detector.update(symbol, 2900.0, now + 1000)
        
        assert result is not None
        assert result.is_whale_move is True
        assert result.change_percent == -3.33

    def test_window_cleanup(self):
        """Test that old prices fall out of the window."""
        detector = PriceChangeDetector(window_seconds=10, threshold_percent=1.0)
        symbol = "SOLUSDT"
        now = 1000000000
        
        # T=0: 100.0
        detector.update(symbol, 100.0, now)
        
        # T=11s: 100.5 (Old price (T=0) should be removed BEFORE check? 
        # Wait, implementation removes points older than window cutoff.
        # Cutoff = T=11s - 10s = T=1s.
        # So T=0 is REMOVED.
        # If list becomes empty or only has the new point, no comparison against old allowed?
        # Actually logic says: add new point, then clean up.
        # If T=0 is removed, and T=11 is added, list has [T=11].
        # Comparison: current(100.5) vs oldest(100.5) = 0% change.
        
        # Correct verification:
        result = detector.update(symbol, 100.5, now + 11000)
        assert result is None  # Because baseline (100.0) expired


class TestLevelCrossDetector:
    """Test suite for Psychological Levels."""
    
    def test_level_cross_up(self):
        """Test crossing level upwards."""
        detector = LevelCrossDetector(levels=[69000])
        symbol = "BTCUSDT"
        
        # Below
        assert detector.update(symbol, 68000.0) is None
        
        # Crossing UP
        result = detector.update(symbol, 69005.0)
        assert result is not None
        assert result.level == 69000
        assert result.direction == "UP"
        
    def test_level_cross_down(self):
        """Test crossing level downwards."""
        detector = LevelCrossDetector(levels=[69000])
        symbol = "BTCUSDT"
        
        # Above
        detector.update(symbol, 70000.0)
        
        # Crossing DOWN
        result = detector.update(symbol, 68500.0)
        assert result is not None
        assert result.level == 69000
        assert result.direction == "DOWN"
        
    def test_no_cross_same_side(self):
        """Test moving without crossing level."""
        detector = LevelCrossDetector(levels=[70000])
        symbol = "BTCUSDT"
        
        detector.update(symbol, 69000.0)
        assert detector.update(symbol, 69500.0) is None  # Still below
        assert detector.update(symbol, 69999.0) is None  # Still below
