"""
Volume Spike Detection.

Detects abnormal volume spikes that may indicate market movements.
"""
from collections import deque
from dataclasses import dataclass
from typing import Dict


@dataclass
class VolumeResult:
    """Volume analysis result."""
    symbol: str
    current_volume: float
    average_volume: float
    spike_multiplier: float
    is_spike: bool  # > 5x average


class VolumeSpikeDetector:
    """
    Detects volume spikes by comparing to rolling average.
    """
    
    def __init__(self, window_size: int = 100, spike_threshold: float = 5.0):
        """
        Initialize detector.
        
        Args:
            window_size: Number of trades for average calculation
            spike_threshold: Multiplier to consider a spike (default 5x)
        """
        self.window_size = window_size
        self.spike_threshold = spike_threshold
        self.volumes: Dict[str, deque] = {}
        
    def update(self, symbol: str, volume: float) -> VolumeResult:
        """
        Update with new trade volume.
        
        Args:
            symbol: Trading pair symbol
            volume: Trade volume
            
        Returns:
            VolumeResult with spike detection
        """
        if symbol not in self.volumes:
            self.volumes[symbol] = deque(maxlen=self.window_size)
            
        volumes = self.volumes[symbol]
        
        # Calculate average before adding new volume
        avg_volume = sum(volumes) / len(volumes) if volumes else volume
        
        # Calculate spike multiplier
        multiplier = volume / avg_volume if avg_volume > 0 else 0
        
        # Add to window
        volumes.append(volume)
        
        return VolumeResult(
            symbol=symbol,
            current_volume=round(volume, 8),
            average_volume=round(avg_volume, 8),
            spike_multiplier=round(multiplier, 2),
            is_spike=multiplier > self.spike_threshold,
        )
    
    def get_average(self, symbol: str) -> float | None:
        """Get current average volume for a symbol."""
        if symbol not in self.volumes or not self.volumes[symbol]:
            return None
        volumes = self.volumes[symbol]
        return sum(volumes) / len(volumes)
