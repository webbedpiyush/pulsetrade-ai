"""
Finage WebSocket Ingestor for US/UK market data.

Provides real-time data for:
- US: NYSE, NASDAQ stocks
- UK: LSE stocks
- Forex pairs
- Crypto

Finage uses JSON WebSocket format (unlike Kite's binary).
Free tier: 100 API calls/day
Paid: Real-time WebSocket streaming
"""
import asyncio
from typing import Optional, List, Callable
import json
import websockets
from datetime import datetime


class FinageIngestor:
    """
    Real-time market data from Finage.
    
    Supports:
    - US stocks (AAPL, MSFT, GOOGL, etc.)
    - UK stocks (with .L suffix)
    - Forex (EURUSD, GBPUSD, etc.)
    
    WebSocket URL: wss://ws.finage.co.uk/
    """
    
    WS_URL = "wss://ws.finage.co.uk"
    
    # Popular US stocks (can be customized)
    DEFAULT_US_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "NVDA", "TSLA", "JPM", "V", "JNJ",
        "WMT", "PG", "UNH", "HD", "MA",
    ]
    
    # Popular UK stocks (LSE)
    DEFAULT_UK_SYMBOLS = [
        "SHEL.L", "AZN.L", "HSBA.L", "BP.L", "GSK.L",
        "RIO.L", "ULVR.L", "DGE.L", "LLOY.L", "BARC.L",
    ]
    
    def __init__(
        self, 
        api_key: str,
        tick_queue: asyncio.Queue,
        us_symbols: Optional[List[str]] = None,
        uk_symbols: Optional[List[str]] = None,
        include_forex: bool = False
    ):
        """
        Initialize Finage WebSocket ingestor.
        
        Args:
            api_key: Finage API key
            tick_queue: Queue for decoupled processing
            us_symbols: US stock symbols (default: top 15)
            uk_symbols: UK stock symbols (default: top 10)
            include_forex: Include major forex pairs
        """
        self.api_key = api_key
        self.tick_queue = tick_queue
        self.us_symbols = us_symbols or self.DEFAULT_US_SYMBOLS
        self.uk_symbols = uk_symbols or self.DEFAULT_UK_SYMBOLS
        self.include_forex = include_forex
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = True
        
    def _build_subscription_message(self) -> dict:
        """Build WebSocket subscription message."""
        symbols = []
        
        # Add US stocks
        for s in self.us_symbols:
            symbols.append(f"stocks:{s}")
            
        # Add UK stocks (already have .L suffix)
        for s in self.uk_symbols:
            symbols.append(f"stocks:{s}")
            
        # Add forex if enabled
        if self.include_forex:
            symbols.extend([
                "forex:EURUSD",
                "forex:GBPUSD",
                "forex:USDJPY",
                "forex:USDCAD",
            ])
            
        return {
            "action": "subscribe",
            "symbols": symbols
        }
        
    def _parse_tick(self, data: dict) -> Optional[dict]:
        """
        Parse Finage tick message.
        
        Finage format:
        {
            "s": "AAPL",           # Symbol
            "p": 178.50,           # Price
            "t": 1640000000000,    # Timestamp (ms)
            "v": 1000,             # Volume (optional)
            "dp": 0.5,             # Day change % (optional)
            "T": "stocks"          # Type
        }
        """
        try:
            symbol = data.get('s', '')
            price = data.get('p')
            
            if not symbol or price is None:
                return None
                
            # Determine market prefix
            if symbol.endswith('.L'):
                market_prefix = "LSE"
            else:
                market_prefix = "US"
                
            return {
                "symbol": f"{market_prefix}:{symbol}",
                "ltp": float(price),
                "volume": data.get('v', 0),
                "change_pct": data.get('dp', 0),
                "timestamp": data.get('t'),
            }
        except Exception as e:
            return None
            
    async def connect(self):
        """
        Connect to Finage WebSocket and start receiving data.
        Includes automatic reconnection with exponential backoff.
        """
        reconnect_delay = 1
        max_delay = 60
        
        print(f"Finage ingestor starting...")
        print(f"US stocks: {len(self.us_symbols)}")
        print(f"UK stocks: {len(self.uk_symbols)}")
        
        while self._running:
            try:
                url = f"{self.WS_URL}?token={self.api_key}"
                
                async with websockets.connect(url) as ws:
                    self.ws = ws
                    print("✅ Finage WebSocket connected!")
                    
                    # Reset reconnect delay on successful connection
                    reconnect_delay = 1
                    
                    # Subscribe to symbols
                    sub_msg = self._build_subscription_message()
                    await ws.send(json.dumps(sub_msg))
                    print(f"Subscribed to {len(sub_msg['symbols'])} symbols")
                    
                    # Receive messages
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            
                            # Handle different message types
                            if isinstance(data, list):
                                # Batch of ticks
                                for tick_data in data:
                                    tick = self._parse_tick(tick_data)
                                    if tick:
                                        try:
                                            self.tick_queue.put_nowait(tick)
                                        except asyncio.QueueFull:
                                            pass
                            elif isinstance(data, dict):
                                # Single tick or status message
                                if 's' in data:
                                    tick = self._parse_tick(data)
                                    if tick:
                                        try:
                                            self.tick_queue.put_nowait(tick)
                                        except asyncio.QueueFull:
                                            pass
                                elif 'status' in data:
                                    print(f"Finage status: {data.get('message', data)}")
                                    
                        except json.JSONDecodeError:
                            pass
                            
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Finage connection closed: {e}")
            except Exception as e:
                print(f"Finage error: {e}")
                
            if self._running:
                print(f"Reconnecting to Finage in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_delay)
                
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self._running = False
        if self.ws:
            await self.ws.close()
            
    def stop(self):
        """Stop the ingestor."""
        self._running = False
