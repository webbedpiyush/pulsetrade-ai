"""
Kite Connect WebSocket Ingestor for NSE (India) market data.

Handles binary packet parsing for high-frequency tick data.
Uses asyncio.Queue for backpressure handling.
"""
import struct
import asyncio
from decimal import Decimal
from typing import Optional
import websockets
import orjson


class KiteTickerIngestor:
    """
    NSE market data ingestor via Kite Connect WebSocket.
    
    CRITICAL: Uses asyncio.Queue to decouple ingestion from processing.
    This prevents backpressure when ticks arrive in microsecond bursts.
    
    Binary packet modes:
    - LTP: 8 bytes (Last Traded Price only)
    - Quote: 44 bytes (with OHLC)
    - Full: 184 bytes (with market depth)
    """
    
    WS_URL = "wss://ws.kite.trade"
    
    # Mode byte sizes
    MODE_LTP = "ltp"      # 8 bytes
    MODE_QUOTE = "quote"  # 44 bytes
    MODE_FULL = "full"    # 184 bytes
    
    def __init__(
        self, 
        api_key: str, 
        access_token: str, 
        tick_queue: asyncio.Queue,
        instrument_map: Optional[dict] = None
    ):
        """
        Initialize Kite Ticker.
        
        Args:
            api_key: Kite Connect API key
            access_token: Session access token
            tick_queue: Queue for decoupled processing
            instrument_map: Optional mapping of token -> symbol name
        """
        self.api_key = api_key
        self.access_token = access_token
        self.tick_queue = tick_queue
        self.instrument_map = instrument_map or {}
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60
        
    def _parse_binary_packet(self, data: bytes) -> Optional[dict]:
        """
        Parse binary packet from Kite Ticker.
        
        Returns:
            Parsed tick dict or None if invalid
        """
        if len(data) < 8:
            return None
            
        # First 4 bytes: Instrument token (Little Endian unsigned int)
        instrument_token = struct.unpack("<I", data[0:4])[0]
        
        # Bytes 4-8: Last traded price (divide by 100 for decimal)
        raw_ltp = struct.unpack("<I", data[4:8])[0]
        ltp = Decimal(raw_ltp) / 100
        
        # Get symbol name from instrument map, fallback to token
        symbol = self.instrument_map.get(
            instrument_token, 
            str(instrument_token)
        )
        
        result = {
            "instrument_token": instrument_token,
            "symbol": f"NSE:{symbol}",
            "ltp": ltp,
            "mode": "ltp"
        }
        
        if len(data) >= 44:
            # Quote mode: includes OHLC
            result["volume"] = struct.unpack("<I", data[16:20])[0]
            result["mode"] = "quote"
            
        if len(data) >= 184:
            # Full mode: includes market depth
            result["mode"] = "full"
            # Parse market depth if needed (bytes 88-184)
            
        return result
    
    async def _handle_messages(self):
        """
        Non-blocking message handler.
        Pushes parsed ticks to queue (load shedding if full).
        """
        while True:
            try:
                data = await self.ws.recv()
                
                # Skip text messages (heartbeat, etc.)
                if isinstance(data, str):
                    continue
                    
                parsed = self._parse_binary_packet(data)
                if parsed:
                    try:
                        self.tick_queue.put_nowait(parsed)
                    except asyncio.QueueFull:
                        # Load shedding: drop ticks rather than lag
                        print(f"WARNING: Dropping tick for {parsed.get('symbol')} - queue full")
                        
            except websockets.ConnectionClosed:
                raise
            except Exception as e:
                print(f"Error parsing packet: {e}")
    
    async def connect(self):
        """
        Connect to Kite WebSocket with auto-reconnect.
        Uses exponential backoff on connection failures.
        """
        url = f"{self.WS_URL}?api_key={self.api_key}&access_token={self.access_token}"
        
        while True:
            try:
                print(f"Connecting to Kite Ticker...")
                async with websockets.connect(url) as ws:
                    self.ws = ws
                    self._reconnect_delay = 1  # Reset on successful connect
                    print("Connected to Kite Ticker!")
                    await self._handle_messages()
                    
            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e}")
            except Exception as e:
                print(f"Connection error: {e}")
                
            # Exponential backoff
            print(f"Reconnecting in {self._reconnect_delay}s...")
            await asyncio.sleep(self._reconnect_delay)
            self._reconnect_delay = min(
                self._reconnect_delay * 2, 
                self._max_reconnect_delay
            )
                
    async def subscribe(self, instrument_tokens: list, mode: str = "full"):
        """
        Subscribe to instruments.
        
        Args:
            instrument_tokens: List of NSE instrument tokens
            mode: "ltp", "quote", or "full"
        """
        if not self.ws:
            print("Not connected. Cannot subscribe.")
            return
            
        await self.ws.send(orjson.dumps({
            "a": "subscribe",
            "v": instrument_tokens
        }))
        await self.ws.send(orjson.dumps({
            "a": "mode",
            "v": [mode, instrument_tokens]
        }))
        print(f"Subscribed to {len(instrument_tokens)} instruments in {mode} mode")
