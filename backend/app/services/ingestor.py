"""
Binance WebSocket Ingestor -> Confluent Kafka Producer.

Connects to Binance public trade stream and produces events to Kafka.
"""
import asyncio
import json
import websockets
from typing import Callable, Awaitable
from ddtrace import tracer

from app.core.kafka import get_producer, TOPIC_CRYPTO_TRADES
from app.models.trade import TradeEvent


# Tracked symbols
TRACKED_SYMBOLS = ["btcusdt", "ethusdt", "solusdt"]

# Binance WebSocket URL (Using Binance US to avoid HTTP 451 Geo-blocking on Railway)
BINANCE_WS_URL = "wss://stream.binance.us:9443/ws/" + "/".join(
    f"{symbol}@trade" for symbol in TRACKED_SYMBOLS
)


class BinanceIngestor:
    """
    Ingests trade data from Binance WebSocket and produces to Kafka.
    """
    
    def __init__(self):
        self.producer = get_producer()
        self.running = False
        self.message_count = 0
        
        # Callback to broadcast trades to frontend
        self.on_trade: Callable[[TradeEvent], Awaitable[None]] | None = None
        
    async def start(self):
        """Start the ingestor (runs forever)."""
        self.running = True
        print(f"[Ingestor] STARTING... Target: {BINANCE_WS_URL}")
        
        while self.running:
            try:
                print(f"[Ingestor] Attempting connection...")
                await self._connect_and_stream()
            except Exception as e:
                print(f"[Ingestor] CRITICAL Connection error: {e}")
                if self.running:
                    print("[Ingestor] Reconnecting in 5s...")
                    await asyncio.sleep(5)
    
    async def _connect_and_stream(self):
        """Connect to Binance and stream trades."""
        print("[Ingestor] Opening WebSocket connection...")
        async with websockets.connect(BINANCE_WS_URL) as ws:
            print("[Ingestor] SUCCESS: Connected to Binance WebSocket")
            
            while self.running:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30)
                    # print(f"[Ingestor] Raw message received: {msg[:50]}...") # Optional debug
                    await self._process_message(msg)
                except asyncio.TimeoutError:
                    print("[Ingestor] Timeout - sending ping")
                    # Send ping to keep alive
                    await ws.ping()
                    
    async def _process_message(self, msg: str):
        """Process a Binance trade message."""
        data = json.loads(msg)
        
        # Parse to our model
        trade = TradeEvent.from_binance(data)
        
        # Produce to Kafka with tracing
        with tracer.trace("kafka.produce", service="pulsetrade-ingestor") as span:
            span.set_tag("symbol", trade.symbol)
            span.set_tag("price", trade.price)
            
            self.producer.produce(
                topic=TOPIC_CRYPTO_TRADES,
                key=trade.symbol.encode(),
                value=trade.to_kafka_bytes(),
            )
        
        # Broadcast to frontend (No throttling for debug)
        if self.on_trade:
             # print(f"[Debug] Ingestor dispatching {trade.symbol} {trade.price}")
             await self.on_trade(trade)
            
        self.message_count += 1
        
        # Flush periodically (every 100 messages)
        if self.message_count % 100 == 0:
            self.producer.poll(0)
            print(f"[Ingestor] Processed {self.message_count} trades")
            
    def stop(self):
        """Stop the ingestor."""
        self.running = False
        self.producer.flush()
        print("[Ingestor] Stopped")


# Singleton instance
_ingestor: BinanceIngestor | None = None


def get_ingestor() -> BinanceIngestor:
    """Get singleton ingestor instance."""
    global _ingestor
    if _ingestor is None:
        _ingestor = BinanceIngestor()
    return _ingestor
