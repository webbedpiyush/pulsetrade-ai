"""
Yahoo Finance Ingestor for NSE market data.

Fetches all NIFTY 50 constituents from NSE India API or uses complete hardcoded list.
"""
import asyncio
from decimal import Decimal
from typing import Optional, List
import yfinance as yf
import pandas as pd
import httpx


class YahooFinanceIngestor:
    """
    Free NSE market data via Yahoo Finance.
    
    Fetches NIFTY 50 constituents dynamically from NSE India,
    with a complete fallback list.
    """
    
    NSE_NIFTY50_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    
    # Complete NIFTY 50 list (as of Dec 2024) - used as fallback
    NIFTY50_SYMBOLS = [
        "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
        "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BPCL",
        "BHARTIARTL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY",
        "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
        "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
        "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT",
        "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
        "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN",
        "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
        "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO",
    ]
    
    def __init__(
        self, 
        tick_queue: asyncio.Queue,
        symbols: Optional[List[str]] = None,
        poll_interval: float = 5.0
    ):
        """
        Initialize Yahoo Finance ingestor.
        
        Args:
            tick_queue: Queue for decoupled processing
            symbols: Optional list of symbols (will use NIFTY 50 if None)
            poll_interval: Seconds between API polls
        """
        self.tick_queue = tick_queue
        self.symbols = symbols
        self.poll_interval = poll_interval
        self._running = True
        
    async def _fetch_nifty50_from_nse(self) -> List[str]:
        """
        Try to fetch live NIFTY 50 constituents from NSE India.
        
        Returns:
            List of Yahoo Finance symbols (e.g., "RELIANCE.NS")
        """
        try:
            print("📥 Fetching NIFTY 50 from NSE India...")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }
            
            async with httpx.AsyncClient() as client:
                # First get cookies from main page
                await client.get("https://www.nseindia.com", headers=headers)
                
                # Then fetch the API
                response = await client.get(self.NSE_NIFTY50_URL, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    symbols = [item['symbol'] for item in data.get('data', [])]
                    # Filter out the index itself (e.g., "NIFTY 50") - only keep actual stocks
                    symbols = [s for s in symbols if s and not s.startswith("NIFTY")]
                    if symbols:
                        yahoo_symbols = [f"{s}.NS" for s in symbols]
                        print(f"✅ Fetched {len(yahoo_symbols)} stocks from NSE India")
                        return yahoo_symbols
                        
        except Exception as e:
            print(f"⚠️ NSE India API failed: {e}")
            
        return []
        
    def _symbol_to_nse(self, yahoo_symbol: str) -> str:
        """Convert Yahoo symbol (RELIANCE.NS) to NSE format (NSE:RELIANCE)."""
        base = yahoo_symbol.replace(".NS", "").replace(".BO", "")
        return f"NSE:{base}"
        
    async def connect(self):
        """
        Start polling Yahoo Finance for price updates.
        Runs indefinitely until stopped.
        """
        # Try to fetch from NSE, fallback to hardcoded list
        if not self.symbols:
            nse_symbols = await self._fetch_nifty50_from_nse()
            
            if nse_symbols:
                self.symbols = nse_symbols
            else:
                # Use the complete hardcoded NIFTY 50 list
                print("📋 Using complete NIFTY 50 list (50 stocks)")
                self.symbols = [f"{s}.NS" for s in self.NIFTY50_SYMBOLS]
            
        print(f"Yahoo Finance ingestor started!")
        print(f"Tracking {len(self.symbols)} NSE stocks")
        print(f"Poll interval: {self.poll_interval}s (data delayed ~15min)")
        
        while self._running:
            try:
                prices = await asyncio.to_thread(self._fetch_prices_sync)
                
                for symbol, data in prices.items():
                    try:
                        self.tick_queue.put_nowait(data)
                    except asyncio.QueueFull:
                        pass  # Drop if queue full
                        
                if prices:
                    print(f"📈 Yahoo: Fetched {len(prices)} stocks")
                    
            except Exception as e:
                print(f"Yahoo fetch error: {e}")
                
            await asyncio.sleep(self.poll_interval)
            
    def _fetch_prices_sync(self) -> dict:
        """Synchronous batch download for efficiency."""
        prices = {}
        
        try:
            # Batch download all symbols at once
            data = yf.download(
                self.symbols, 
                period="1d", 
                interval="1m",
                progress=False,
                threads=True,
                auto_adjust=True
            )
            
            if len(data) > 0:
                for symbol in self.symbols:
                    try:
                        if len(self.symbols) == 1:
                            close_prices = data['Close']
                        else:
                            if symbol in data['Close'].columns:
                                close_prices = data['Close'][symbol]
                            else:
                                continue
                            
                        if close_prices is not None and len(close_prices) > 0:
                            price = close_prices.iloc[-1]
                            if pd.notna(price) and price > 0:
                                prices[symbol] = {
                                    "symbol": self._symbol_to_nse(symbol),
                                    "ltp": round(float(price), 2),
                                    "volume": 0,
                                }
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"Batch download failed: {e}")
                    
        return prices
        
    def stop(self):
        """Stop the ingestor."""
        self._running = False
