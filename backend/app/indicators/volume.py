"""
Volume Spike Detection.

Uses 1-second time windows to aggregate volume before comparing to average.
This prevents high-frequency tick noise from causing false volume spikes.
"""
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class VolumeResult:
    """Volume analysis result."""
    symbol: str
    current_volume: float
    average_volume: float
    spike_multiplier: float
    is_spike: bool  # > threshold (default 5x average)


class TimeBasedVolumeAggregator:
    """
    Aggregates volume into 1-second windows.
    
    Instead of comparing individual tick volumes (which are tiny and noisy),
    we aggregate all volume within each second and compare the total.
    """
    
    def __init__(self, window_size: int = 30, spike_threshold: float = 5.0):
        """
        Initialize aggregator.
        
        Args:
            window_size: Number of 1-second windows for average calculation
            spike_threshold: Multiplier to consider a spike (default 5x)
        """
        self.window_size = window_size
        self.spike_threshold = spike_threshold
        
        # Store aggregated volume per 1-second window
        self.window_volumes: deque = deque(maxlen=window_size)
        self.current_window_volume: float = 0.0
        self.last_window_time: int = 0
        
    def add_tick(self, volume: float, timestamp_ms: int) -> Optional[VolumeResult]:
        """
        Process a tick and return result if a new 1-second window completed.
        
        Args:
            volume: Trade volume
            timestamp_ms: Trade timestamp in milliseconds
            
        Returns:
            VolumeResult if a new 1-second window completed, None otherwise
        """
        current_second = timestamp_ms // 1000
        
        # First tick ever
        if self.last_window_time == 0:
            self.last_window_time = current_second
            self.current_window_volume = volume
            return None
        
        # New second? Complete the previous window
        if current_second > self.last_window_time:
            # Save the completed window's volume
            completed_volume = self.current_window_volume
            self.window_volumes.append(completed_volume)
            
            # Start new window
            self.current_window_volume = volume
            self.last_window_time = current_second
            
            # Calculate if we have enough history
            if len(self.window_volumes) >= 5:  # Need at least 5 seconds of history
                return self._calculate_spike(completed_volume)
        else:
            # Same second - accumulate volume
            self.current_window_volume += volume
            
        return None
    
    def _calculate_spike(self, current_volume: float) -> VolumeResult:
        """Calculate whether the completed window is a volume spike."""
        # Average of previous windows (excluding current)
        previous_volumes = list(self.window_volumes)[:-1]  # Exclude the one we just added
        
        if not previous_volumes:
            avg_volume = current_volume
        else:
            avg_volume = sum(previous_volumes) / len(previous_volumes)
        
        # Calculate spike multiplier
        multiplier = current_volume / avg_volume if avg_volume > 0 else 0
        
        return VolumeResult(
            symbol="",  # Will be set by caller
            current_volume=round(current_volume, 8),
            average_volume=round(avg_volume, 8),
            spike_multiplier=round(multiplier, 2),
            is_spike=multiplier > self.spike_threshold,
        )


class VolumeSpikeDetector:
    """
    Multi-symbol volume spike detector using time-based aggregation.
    """
    
    def __init__(self, window_size: int = 30, spike_threshold: float = 5.0):
        """
        Initialize detector.
        
        Args:
            window_size: Number of 1-second windows for average calculation
            spike_threshold: Multiplier to consider a spike (default 5x)
        """
        self.window_size = window_size
        self.spike_threshold = spike_threshold
        self.aggregators: Dict[str, TimeBasedVolumeAggregator] = {}
        
    def update(self, symbol: str, volume: float, timestamp_ms: int = None) -> VolumeResult:
        """
        Update with new trade volume.
        
        Args:
            symbol: Trading pair symbol
            volume: Trade volume
            timestamp_ms: Trade timestamp in milliseconds
            
        Returns:
            VolumeResult if a 1-second window completed, None otherwise
        """
        import time
        
        if timestamp_ms is None:
            timestamp_ms = int(time.time() * 1000)
            
        if symbol not in self.aggregators:
            self.aggregators[symbol] = TimeBasedVolumeAggregator(
                window_size=self.window_size,
                spike_threshold=self.spike_threshold
            )
            
        result = self.aggregators[symbol].add_tick(volume, timestamp_ms)
        
        if result:
            result.symbol = symbol
            return result
            
        return None
    
    def get_average(self, symbol: str) -> float | None:
        """Get current average volume for a symbol."""
        if symbol not in self.aggregators:
            return None
            
        agg = self.aggregators[symbol]
        if not agg.window_volumes:
            return None
            
        return sum(agg.window_volumes) / len(agg.window_volumes)
