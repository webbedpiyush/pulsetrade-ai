"""
Redis State Management for PulseTrade AI.

Provides:
- Tick data caching (last N ticks per symbol)
- Price history for charts
- Alert deduplication
- Pub/Sub for real-time updates
"""
import asyncio
from typing import Optional, List, Dict, Any
import json
import redis.asyncio as redis
from datetime import datetime, timedelta


class RedisStateManager:
    """
    High-performance state management using Redis.
    
    Features:
    - O(1) tick updates
    - Sliding window price history
    - Alert rate limiting
    - Pub/Sub for multi-instance support
    """
    
    # Key prefixes
    TICK_PREFIX = "tick:"           # Latest tick per symbol
    HISTORY_PREFIX = "history:"     # Price history (sorted set)
    ALERT_PREFIX = "alert:"         # Recent alerts for deduplication
    INDICATOR_PREFIX = "ind:"       # Technical indicators
    
    # TTLs
    TICK_TTL = 60                   # Ticks expire after 1 min
    HISTORY_TTL = 3600              # History expires after 1 hour
    ALERT_COOLDOWN = 30             # Alert dedup window (seconds)
    
    # Limits
    MAX_HISTORY_POINTS = 500        # Max price points per symbol
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        db: int = 0
    ):
        """
        Initialize Redis connection.
        
        Args:
            redis_url: Redis connection URL
            db: Redis database number
        """
        self.redis_url = redis_url
        self.db = db
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        
    async def connect(self):
        """Establish Redis connection."""
        try:
            self.client = redis.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=True
            )
            await self.client.ping()
            print(f"✅ Redis connected: {self.redis_url}")
            return True
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("   Running without Redis (in-memory mode)")
            self.client = None
            return False
            
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            
    # =========================================================================
    # Tick Storage
    # =========================================================================
    
    async def save_tick(self, symbol: str, tick_data: dict) -> bool:
        """
        Save latest tick for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "NSE:RELIANCE")
            tick_data: Tick data dict with price, volume, etc.
        """
        if not self.client:
            return False
            
        try:
            key = f"{self.TICK_PREFIX}{symbol}"
            tick_data['timestamp'] = datetime.utcnow().isoformat()
            
            await self.client.set(
                key,
                json.dumps(tick_data),
                ex=self.TICK_TTL
            )
            return True
        except Exception as e:
            print(f"Redis save_tick error: {e}")
            return False
            
    async def get_tick(self, symbol: str) -> Optional[dict]:
        """Get latest tick for a symbol."""
        if not self.client:
            return None
            
        try:
            key = f"{self.TICK_PREFIX}{symbol}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
            
    async def get_all_ticks(self) -> Dict[str, dict]:
        """Get all current ticks."""
        if not self.client:
            return {}
            
        try:
            keys = await self.client.keys(f"{self.TICK_PREFIX}*")
            if not keys:
                return {}
                
            result = {}
            for key in keys:
                data = await self.client.get(key)
                if data:
                    symbol = key.replace(self.TICK_PREFIX, "")
                    result[symbol] = json.loads(data)
            return result
        except Exception:
            return {}
            
    # =========================================================================
    # Price History (for Charts)
    # =========================================================================
    
    async def add_price_point(self, symbol: str, price: float, timestamp: Optional[float] = None) -> bool:
        """
        Add price point to history (sorted set by timestamp).
        
        Args:
            symbol: Stock symbol
            price: Current price
            timestamp: Unix timestamp (defaults to now)
        """
        if not self.client:
            return False
            
        try:
            key = f"{self.HISTORY_PREFIX}{symbol}"
            ts = timestamp or datetime.utcnow().timestamp()
            
            # Add to sorted set (score = timestamp, value = price:timestamp)
            await self.client.zadd(key, {f"{price}:{ts}": ts})
            
            # Trim to max size
            await self.client.zremrangebyrank(key, 0, -self.MAX_HISTORY_POINTS - 1)
            
            # Set TTL
            await self.client.expire(key, self.HISTORY_TTL)
            
            return True
        except Exception as e:
            print(f"Redis add_price_point error: {e}")
            return False
            
    async def get_price_history(self, symbol: str, limit: int = 100) -> List[dict]:
        """
        Get price history for charting.
        
        Returns:
            List of {time, value} dicts
        """
        if not self.client:
            return []
            
        try:
            key = f"{self.HISTORY_PREFIX}{symbol}"
            # Get latest N entries
            data = await self.client.zrevrange(key, 0, limit - 1, withscores=True)
            
            history = []
            for value, score in reversed(data):
                price_str = value.split(":")[0]
                history.append({
                    "time": int(score),
                    "value": float(price_str)
                })
            return history
        except Exception:
            return []
            
    # =========================================================================
    # Alert Deduplication
    # =========================================================================
    
    async def should_send_alert(self, symbol: str, direction: str) -> bool:
        """
        Check if alert should be sent (rate limiting).
        
        Prevents spam by ensuring only one alert per symbol
        per cooldown period.
        """
        if not self.client:
            return True  # Always send if no Redis
            
        try:
            key = f"{self.ALERT_PREFIX}{symbol}:{direction}"
            
            # Try to set key (only succeeds if not exists)
            was_set = await self.client.set(
                key,
                "1",
                ex=self.ALERT_COOLDOWN,
                nx=True
            )
            return was_set is not None
        except Exception:
            return True
            
    # =========================================================================
    # Technical Indicators Cache
    # =========================================================================
    
    async def save_indicators(self, symbol: str, indicators: dict) -> bool:
        """Save technical indicators for a symbol."""
        if not self.client:
            return False
            
        try:
            key = f"{self.INDICATOR_PREFIX}{symbol}"
            await self.client.set(
                key,
                json.dumps(indicators),
                ex=self.TICK_TTL
            )
            return True
        except Exception:
            return False
            
    async def get_indicators(self, symbol: str) -> Optional[dict]:
        """Get cached technical indicators."""
        if not self.client:
            return None
            
        try:
            key = f"{self.INDICATOR_PREFIX}{symbol}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
            
    # =========================================================================
    # Pub/Sub for Multi-Instance Support
    # =========================================================================
    
    async def publish_tick(self, symbol: str, tick_data: dict):
        """Publish tick update to subscribers."""
        if not self.client:
            return
            
        try:
            channel = f"ticks:{symbol}"
            await self.client.publish(channel, json.dumps(tick_data))
        except Exception:
            pass
            
    async def subscribe_ticks(self, symbols: List[str], callback):
        """Subscribe to tick updates for symbols."""
        if not self.client:
            return
            
        try:
            self.pubsub = self.client.pubsub()
            channels = [f"ticks:{s}" for s in symbols]
            await self.pubsub.subscribe(*channels)
            
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await callback(data)
        except Exception as e:
            print(f"PubSub error: {e}")


# Global instance
redis_state: Optional[RedisStateManager] = None


async def get_redis_state() -> RedisStateManager:
    """Get or create Redis state manager using settings."""
    global redis_state
    if redis_state is None:
        from app.config import Settings
        settings = Settings()
        redis_state = RedisStateManager(redis_url=settings.REDIS_URL)
        await redis_state.connect()
    return redis_state
