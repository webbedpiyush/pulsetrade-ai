"""
Yahoo Finance Ingestor for Global Market Data.

Fetches stock data from:
- India (NSE): NIFTY 50 constituents (from NSE API or fallback)
- US (NYSE/NASDAQ): S&P 500 constituents (from Wikipedia)
- UK (LSE): FTSE 100 constituents (from Wikipedia)
"""
import asyncio
import warnings
import logging
from decimal import Decimal
from typing import Optional, List, Dict

# Suppress all warnings from yfinance (timeouts, deprecations, etc.)
warnings.filterwarnings('ignore')

# Suppress yfinance logging (timeout errors, failed downloads)
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('peewee').setLevel(logging.CRITICAL)

import yfinance as yf
import pandas as pd
import httpx

class YahooFinanceIngestor:
    """
    Global market data via Yahoo Finance.
    
    Dynamically fetches index constituents:
    - NIFTY 50 from NSE India API
    - S&P 500 from Wikipedia
    - FTSE 100 from Wikipedia
    
    Data is ~15 min delayed (Yahoo Finance limitation).
    """
    
    # API/Wikipedia URLs for dynamic fetching
    NSE_NIFTY50_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    FTSE100_WIKI_URL = "https://en.wikipedia.org/wiki/FTSE_100_Index"
    
    # Fallback lists (used if Wikipedia scraping fails)
    NIFTY50_FALLBACK = [
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
    
    SP500_FALLBACK = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "UNH", "JNJ", "V", "XOM", "WMT", "JPM", "MA", "PG", "HD", "CVX",
    ]
    
    FTSE100_FALLBACK = [
        "SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L",
        "RIO.L", "GSK.L", "DGE.L", "BATS.L", "REL.L",
    ]
    
    def __init__(
        self, 
        tick_queue: asyncio.Queue,
        symbols: Optional[List[str]] = None,
        poll_interval: float = 5.0,
        include_india: bool = True,
        include_us: bool = True,
        include_uk: bool = True,
    ):
        """
        Initialize Yahoo Finance ingestor.
        
        Args:
            tick_queue: Queue for decoupled processing
            symbols: Optional custom list of symbols (overrides market flags)
            poll_interval: Seconds between API polls
            include_india: Include NIFTY 50 stocks
            include_us: Include US stocks
            include_uk: Include UK stocks
        """
        self.tick_queue = tick_queue
        self.symbols = symbols
        self.poll_interval = poll_interval
        self.include_india = include_india
        self.include_us = include_us
        self.include_uk = include_uk
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
    
    def _fetch_sp500_from_wikipedia(self) -> List[str]:
        """
        Fetch S&P 500 constituents from Wikipedia.
        
        Returns:
            List of Yahoo Finance symbols (e.g., "AAPL", "MSFT")
        """
        try:
            print("📥 Fetching S&P 500 from Wikipedia...")
            
            # Use requests with proper headers to avoid 403
            import io
            import requests
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(self.SP500_WIKI_URL, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML tables
            tables = pd.read_html(io.StringIO(response.text))
            
            # The first table contains the constituents
            df = tables[0]
            
            # The 'Symbol' column contains the tickers
            if 'Symbol' in df.columns:
                symbols = df['Symbol'].tolist()
            elif 'Ticker' in df.columns:
                symbols = df['Ticker'].tolist()
            else:
                # Try first column
                symbols = df.iloc[:, 0].tolist()
            
            # Clean up symbols (replace dots with dashes for Yahoo compatibility)
            symbols = [str(s).replace('.', '-') for s in symbols if pd.notna(s)]
            
            print(f"✅ Fetched {len(symbols)} S&P 500 stocks from Wikipedia")
            return symbols
            
        except Exception as e:
            print(f"⚠️ Wikipedia S&P 500 fetch failed: {e}")
            return []
    
    def _fetch_ftse100_from_wikipedia(self) -> List[str]:
        """
        Fetch FTSE 100 constituents from Wikipedia.
        
        Returns:
            List of Yahoo Finance symbols with .L suffix (e.g., "SHEL.L")
        """
        try:
            print("📥 Fetching FTSE 100 from Wikipedia...")
            
            # Use requests with proper headers to avoid 403
            import io
            import requests
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(self.FTSE100_WIKI_URL, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML tables
            tables = pd.read_html(io.StringIO(response.text))
            
            # Find the table with the constituents (usually has 'Ticker' or 'EPIC' column)
            for table in tables:
                cols = [str(c).lower() for c in table.columns]
                if 'ticker' in cols or 'epic' in cols or 'company' in cols:
                    df = table
                    break
            else:
                # Use the largest table as fallback
                df = max(tables, key=len)
            
            # Try to find the ticker column
            ticker_col = None
            for col in df.columns:
                if 'ticker' in str(col).lower() or 'epic' in str(col).lower():
                    ticker_col = col
                    break
            
            if ticker_col:
                symbols = df[ticker_col].tolist()
            else:
                # Try the second column (often has tickers)
                symbols = df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
            
            # Clean up and add .L suffix for LSE
            clean_symbols = []
            for s in symbols:
                if pd.notna(s) and isinstance(s, str):
                    s = s.strip().upper()
                    if s and not s.endswith('.L'):
                        s = f"{s}.L"
                    clean_symbols.append(s)
            
            print(f"✅ Fetched {len(clean_symbols)} FTSE 100 stocks from Wikipedia")
            return clean_symbols
            
        except Exception as e:
            print(f"⚠️ Wikipedia FTSE 100 fetch failed: {e}")
            return []
    
    def _normalize_symbol(self, yahoo_symbol: str) -> Dict[str, str]:
        """
        Convert Yahoo symbol to normalized format with market prefix.
        
        Returns:
            Dict with 'symbol' (normalized) and 'market' keys
        """
        if yahoo_symbol.endswith(".NS"):
            base = yahoo_symbol.replace(".NS", "")
            return {"symbol": f"NSE:{base}", "market": "NSE", "currency": "INR"}
        elif yahoo_symbol.endswith(".BO"):
            base = yahoo_symbol.replace(".BO", "")
            return {"symbol": f"BSE:{base}", "market": "BSE", "currency": "INR"}
        elif yahoo_symbol.endswith(".L"):
            base = yahoo_symbol.replace(".L", "")
            return {"symbol": f"LSE:{base}", "market": "LSE", "currency": "GBP"}
        else:
            # US stocks have no suffix
            return {"symbol": f"NYSE:{yahoo_symbol}", "market": "NYSE", "currency": "USD"}
        
    async def connect(self):
        """
        Start polling Yahoo Finance for price updates.
        Runs indefinitely until stopped.
        """
        # Build symbol list if not provided
        if not self.symbols:
            all_symbols = []
            
            # India
            if self.include_india:
                nse_symbols = await self._fetch_nifty50_from_nse()
                if nse_symbols:
                    all_symbols.extend(nse_symbols)
                else:
                    print("📋 Using NIFTY 50 fallback list (50 stocks)")
                    all_symbols.extend([f"{s}.NS" for s in self.NIFTY50_FALLBACK])
            
            # US - Fetch S&P 500 from Wikipedia
            if self.include_us:
                sp500_symbols = await asyncio.to_thread(self._fetch_sp500_from_wikipedia)
                if sp500_symbols:
                    all_symbols.extend(sp500_symbols)
                else:
                    print(f"📋 Using S&P 500 fallback list ({len(self.SP500_FALLBACK)} stocks)")
                    all_symbols.extend(self.SP500_FALLBACK)
            
            # UK - Fetch FTSE 100 from Wikipedia
            if self.include_uk:
                ftse100_symbols = await asyncio.to_thread(self._fetch_ftse100_from_wikipedia)
                if ftse100_symbols:
                    all_symbols.extend(ftse100_symbols)
                else:
                    print(f"📋 Using FTSE 100 fallback list ({len(self.FTSE100_FALLBACK)} stocks)")
                    all_symbols.extend(self.FTSE100_FALLBACK)
                
            self.symbols = all_symbols
            
        print(f"\n🌍 Yahoo Finance Global Ingestor Started!")
        print(f"   📊 Total stocks: {len(self.symbols)}")
        india_symbols = [s for s in self.symbols if s.endswith('.NS')]
        uk_symbols = [s for s in self.symbols if s.endswith('.L')]
        us_symbols = [s for s in self.symbols if not s.endswith('.NS') and not s.endswith('.L')]
        print(f"   �� India: {len(india_symbols)}")
        print(f"   🇺🇸 US: {len(us_symbols)}")
        print(f"   🇬🇧 UK: {len(uk_symbols)}")
        print(f"   ⏱️  Poll interval: {self.poll_interval}s (data delayed ~15min)\n")
        
        # Store categorized symbols for progressive loading
        self._india_symbols = india_symbols
        self._uk_symbols = uk_symbols
        self._us_symbols = us_symbols
        
        while self._running:
            try:
                # Progressive loading: India first (fastest), then UK, then US
                total_prices = {}
                
                # 1. Fetch India first - should complete in ~2-3 seconds
                if self._india_symbols:
                    india_prices = await asyncio.to_thread(
                        self._fetch_batch_prices, self._india_symbols, "🇮🇳 India"
                    )
                    total_prices.update(india_prices)
                    # Push India to queue immediately
                    for data in india_prices.values():
                        try:
                            self.tick_queue.put_nowait(data)
                        except asyncio.QueueFull:
                            pass
                    if india_prices:
                        print(f"📈 India: {len(india_prices)} stocks loaded")
                
                # 2. Fetch UK second - should complete in ~3-5 seconds
                if self._uk_symbols:
                    uk_prices = await asyncio.to_thread(
                        self._fetch_batch_prices, self._uk_symbols, "🇬🇧 UK"
                    )
                    total_prices.update(uk_prices)
                    # Push UK to queue
                    for data in uk_prices.values():
                        try:
                            self.tick_queue.put_nowait(data)
                        except asyncio.QueueFull:
                            pass
                    if uk_prices:
                        print(f"📈 UK: {len(uk_prices)} stocks loaded")
                
                # 3. Fetch US in batches - takes longer but UI already has India/UK
                if self._us_symbols:
                    us_prices = await asyncio.to_thread(
                        self._fetch_batch_prices, self._us_symbols, "🇺🇸 US"
                    )
                    total_prices.update(us_prices)
                    # Push US to queue
                    for data in us_prices.values():
                        try:
                            self.tick_queue.put_nowait(data)
                        except asyncio.QueueFull:
                            pass
                    if us_prices:
                        print(f"📈 US: {len(us_prices)} stocks loaded")
                
                # Summary
                if total_prices:
                    nse = len([k for k in total_prices if "NSE:" in total_prices[k].get("symbol", "")])
                    nyse = len([k for k in total_prices if "NYSE:" in total_prices[k].get("symbol", "")])
                    lse = len([k for k in total_prices if "LSE:" in total_prices[k].get("symbol", "")])
                    print(f"✅ Total: {len(total_prices)} stocks (🇮🇳{nse} 🇺🇸{nyse} 🇬🇧{lse})")
                    
            except Exception as e:
                print(f"Yahoo fetch error: {e}")
                
            await asyncio.sleep(self.poll_interval)
    
    def _fetch_batch_prices(self, symbols: List[str], market_name: str = "") -> dict:
        """
        Fetch prices for a specific list of symbols.
        
        Optimized for smaller batches (50-100 stocks) with faster timeouts.
        Used for progressive market loading.
        """
        prices = {}
        batch_size = 50  # Larger batches OK for single market
        timeout_seconds = 15  # Shorter timeout for smaller lists
        
        # Split symbols into batches
        batches = [
            symbols[i:i + batch_size] 
            for i in range(0, len(symbols), batch_size)
        ]
        
        for batch in batches:
            try:
                # Try intraday data first
                data = yf.download(
                    batch,
                    period="1d",
                    interval="1m",
                    progress=False,
                    threads=True,
                    auto_adjust=True,
                    timeout=timeout_seconds
                )
                
                symbols_with_data = set()
                
                if len(data) > 0 and 'Close' in data.columns.get_level_values(0):
                    for symbol in batch:
                        try:
                            if len(batch) == 1:
                                close_prices = data['Close']
                            else:
                                if symbol in data['Close'].columns:
                                    close_prices = data['Close'][symbol]
                                else:
                                    continue
                            
                            if close_prices is not None and len(close_prices) > 0:
                                price = close_prices.iloc[-1]
                                if pd.notna(price) and price > 0:
                                    norm = self._normalize_symbol(symbol)
                                    price_val = float(price.iloc[0]) if hasattr(price, 'iloc') else float(price)
                                    prices[symbol] = {
                                        "symbol": norm["symbol"],
                                        "ltp": round(price_val, 2),
                                        "volume": 0,
                                        "market": norm["market"],
                                        "currency": norm["currency"],
                                    }
                                    symbols_with_data.add(symbol)
                        except Exception:
                            pass
                
                # Fallback: daily data for missing symbols
                missing = [s for s in batch if s not in symbols_with_data]
                if missing:
                    try:
                        daily_data = yf.download(
                            missing,
                            period="5d",
                            interval="1d",
                            progress=False,
                            threads=True,
                            auto_adjust=True,
                            timeout=timeout_seconds
                        )
                        
                        if len(daily_data) > 0 and 'Close' in daily_data.columns.get_level_values(0):
                            for symbol in missing:
                                try:
                                    if len(missing) == 1:
                                        close_prices = daily_data['Close']
                                    else:
                                        if symbol in daily_data['Close'].columns:
                                            close_prices = daily_data['Close'][symbol]
                                        else:
                                            continue
                                    
                                    if close_prices is not None and len(close_prices) > 0:
                                        valid = close_prices.dropna()
                                        if len(valid) > 0:
                                            norm = self._normalize_symbol(symbol)
                                            last_price = valid.iloc[-1]
                                            price_val = float(last_price.iloc[0]) if hasattr(last_price, 'iloc') else float(last_price)
                                            prices[symbol] = {
                                                "symbol": norm["symbol"],
                                                "ltp": round(price_val, 2),
                                                "volume": 0,
                                                "market": norm["market"],
                                                "currency": norm["currency"],
                                            }
                                except Exception:
                                    pass
                    except Exception:
                        pass
                        
            except Exception:
                pass  # Continue with next batch
        
        return prices
            
    def _fetch_prices_sync(self) -> dict:
        """
        Fetch prices in smaller batches to avoid timeouts.
        
        Yahoo Finance can timeout with large symbol lists (650+ stocks).
        We use smaller batches, longer timeouts, and retry logic.
        """
        prices = {}
        batch_size = 25  # Smaller batches are more reliable
        max_retries = 2  # Retry failed batches once
        timeout_seconds = 30  # 30 seconds per batch (Yahoo is slow)
        
        # Split symbols into batches
        batches = [
            self.symbols[i:i + batch_size] 
            for i in range(0, len(self.symbols), batch_size)
        ]
        
        for batch_idx, batch in enumerate(batches):
            symbols_with_data = set()
            
            # Retry logic
            for attempt in range(max_retries):
                try:
                    # Try intraday data first
                    data = yf.download(
                        batch,
                        period="1d",
                        interval="1m",
                        progress=False,
                        threads=True,
                        auto_adjust=True,
                        timeout=timeout_seconds
                    )
                    
                    if len(data) > 0 and 'Close' in data.columns.get_level_values(0):
                        for symbol in batch:
                            try:
                                if len(batch) == 1:
                                    close_prices = data['Close']
                                else:
                                    if symbol in data['Close'].columns:
                                        close_prices = data['Close'][symbol]
                                    else:
                                        continue
                                
                                if close_prices is not None and len(close_prices) > 0:
                                    price = close_prices.iloc[-1]
                                    if pd.notna(price) and price > 0:
                                        norm = self._normalize_symbol(symbol)
                                        price_val = float(price.iloc[0]) if hasattr(price, 'iloc') else float(price)
                                        prices[symbol] = {
                                            "symbol": norm["symbol"],
                                            "ltp": round(price_val, 2),
                                            "volume": 0,
                                            "market": norm["market"],
                                            "currency": norm["currency"],
                                        }
                                        symbols_with_data.add(symbol)
                            except Exception:
                                pass
                    
                    # If we got most data, break out of retry loop
                    if len(symbols_with_data) >= len(batch) * 0.5:
                        break
                        
                except Exception:
                    if attempt < max_retries - 1:
                        continue  # Retry
                    # Final attempt failed, continue to next batch
            
            # Fallback: fetch daily data for symbols that failed
            missing = [s for s in batch if s not in symbols_with_data]
            
            if missing:
                try:
                    daily_data = yf.download(
                        missing,
                        period="5d",
                        interval="1d",
                        progress=False,
                        threads=True,
                        auto_adjust=True,
                        timeout=timeout_seconds
                    )
                    
                    if len(daily_data) > 0 and 'Close' in daily_data.columns.get_level_values(0):
                        for symbol in missing:
                            try:
                                if len(missing) == 1:
                                    close_prices = daily_data['Close']
                                else:
                                    if symbol in daily_data['Close'].columns:
                                        close_prices = daily_data['Close'][symbol]
                                    else:
                                        continue
                                
                                if close_prices is not None and len(close_prices) > 0:
                                    valid = close_prices.dropna()
                                    if len(valid) > 0:
                                        norm = self._normalize_symbol(symbol)
                                        last_price = valid.iloc[-1]
                                        price_val = float(last_price.iloc[0]) if hasattr(last_price, 'iloc') else float(last_price)
                                        prices[symbol] = {
                                            "symbol": norm["symbol"],
                                            "ltp": round(price_val, 2),
                                            "volume": 0,
                                            "market": norm["market"],
                                            "currency": norm["currency"],
                                        }
                            except Exception:
                                pass
                except Exception:
                    pass  # Ignore daily fallback failures
        
        return prices
        
    def stop(self):
        """Stop the ingestor."""
        self._running = False

