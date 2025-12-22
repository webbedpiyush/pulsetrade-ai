"""
PulseTrade AI - Main Application Entry Point

Orchestrates:
1. Market data ingestion (Yahoo Finance / Kite Connect / Finage)
2. Technical indicator processing
3. Redis state management for low-latency caching
4. WebSocket broadcasting to frontend

Day 1: The Heartbeat - Proving data flows from exchange to backend.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.ingestors.kite import KiteTickerIngestor
from app.ingestors.yahoo import YahooFinanceIngestor
from app.ingestors.finage import FinageIngestor
from app.processors.indicators import IndicatorEngine
from app.state.redis_state import get_redis_state, RedisStateManager


# ============================================================================
# Global State
# ============================================================================

# Queues for decoupled processing (prevents backpressure)
tick_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
alert_queue: asyncio.Queue = asyncio.Queue(maxsize=10)

# Settings loaded from .env
settings = Settings()


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections to frontend clients."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        """Send JSON data to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_bytes(self, data: bytes):
        """Send binary data (audio) to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_bytes(data)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# ============================================================================
# Background Workers
# ============================================================================

async def processing_worker():
    """
    Worker 1: Consumes ticks from queue, calculates indicators.
    Uses Redis for caching and alert deduplication.
    Triggers alerts on breakouts and broadcasts to frontend.
    """
    from app.intelligence.prompts import build_market_alert_prompt
    from app.models.tick import Market
    
    engine = IndicatorEngine()
    tick_count = 0
    
    # Get Redis state manager (gracefully handles if Redis unavailable)
    redis_state = await get_redis_state()
    
    print("Processing worker started...")
    
    while True:
        tick = await tick_queue.get()
        tick_count += 1
        
        # Extract tick data
        symbol = tick.get('symbol', str(tick.get('instrument_token')))
        ltp = float(tick['ltp'])  # Convert Decimal to float for JSON
        volume = tick.get('volume', 0)
        
        # Calculate technical indicators
        snapshot = engine.update(symbol, ltp, volume)
        
        # Save to Redis for caching (non-blocking)
        asyncio.create_task(redis_state.save_tick(symbol, {
            "symbol": symbol,
            "ltp": ltp,
            "volume": volume,
            "sma_5": snapshot.sma_5,
            "volatility": snapshot.volatility,
        }))
        
        # Add to price history for charts
        asyncio.create_task(redis_state.add_price_point(symbol, ltp))
        
        # Log every 100th tick to avoid spam
        if tick_count % 100 == 0:
            print(f"Processed {tick_count} ticks. Latest: {symbol} @ {ltp:.2f}")
        
        # Broadcast tick to frontend
        await manager.broadcast_json({
            "type": "tick",
            "symbol": symbol,
            "price": ltp,
            "volume": volume,
            "breakout": snapshot.is_breakout,
            "direction": snapshot.breakout_direction,
            "sma_5": round(snapshot.sma_5, 2),
            "volatility": round(snapshot.volatility, 4),
        })
        
        # Trigger Gemini + Voice on breakouts (with deduplication)
        if snapshot.is_breakout:
            # Check Redis for alert deduplication (30s cooldown)
            should_alert = await redis_state.should_send_alert(
                symbol, snapshot.breakout_direction
            )
            
            if not should_alert:
                # Skip duplicate alert
                tick_queue.task_done()
                continue
                
            print(f"🚨 BREAKOUT DETECTED: {symbol} {snapshot.breakout_direction} @ {ltp:.2f}")
            
            # Build prompt for Gemini
            prompt = build_market_alert_prompt(
                symbol=symbol,
                price=ltp,
                change_pct=0,  # TODO: Calculate from previous close
                technical={
                    'sma_5': snapshot.sma_5,
                    'volatility': snapshot.volatility,
                    'vwap': snapshot.vwap,
                    'is_breakout': snapshot.is_breakout,
                    'breakout_direction': snapshot.breakout_direction
                },
                market=symbol.split(':')[0] if ':' in symbol else "NSE"
            )
            
            # Push to alert queue for intelligence worker
            try:
                alert_queue.put_nowait({
                    "prompt": prompt,
                    "market": Market.NSE,
                    "symbol": symbol,
                    "price": ltp,
                })
            except asyncio.QueueFull:
                print("Alert queue full - skipping voice alert")
            
        tick_queue.task_done()


async def intelligence_worker():
    """
    Worker 2: Consumes alerts, sends to Gemini, pipes to ElevenLabs.
    Streams audio chunks to frontend.
    
    Day 3 behavior: Saves to file for testing before frontend streaming.
    """
    from app.intelligence.gemini_live import GeminiLiveClient
    from app.voice.synthesizer import ElevenLabsSynthesizer
    from app.voice.voices import get_market_voices
    import time
    import os
    
    # Check if API keys are configured
    if not settings.GEMINI_API_KEY:
        print("⚠️  No Gemini API key. Intelligence worker disabled.")
        return
        
    if not settings.ELEVENLABS_API_KEY:
        print("⚠️  No ElevenLabs API key. Voice synthesis disabled.")
        
    gemini = GeminiLiveClient(settings.GEMINI_API_KEY)
    voice = ElevenLabsSynthesizer(settings.ELEVENLABS_API_KEY) if settings.ELEVENLABS_API_KEY else None
    market_voices = get_market_voices()
    
    await gemini.connect()
    
    # Create output directory for Day 3 testing
    output_dir = "/tmp/pulsetrade_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Intelligence worker started (audio output: {output_dir})...")
    
    while True:
        alert = await alert_queue.get()
        prompt = alert["prompt"]
        market = alert["market"]
        symbol = alert["symbol"]
        
        voice_config = market_voices.get(market, market_voices[list(market_voices.keys())[0]])
        
        print(f"🧠 Generating analysis for {symbol}...")
        
        try:
            # Generate text from Gemini
            analysis = await gemini.generate(prompt)
            print(f"📝 Gemini: {analysis[:100]}...")
            
            # Broadcast text to frontend
            await manager.broadcast_json({
                "type": "analysis",
                "symbol": symbol,
                "text": analysis,
            })
            
            # Synthesize voice if ElevenLabs is configured
            if voice:
                timestamp = int(time.time())
                filename = f"{output_dir}/alert_{symbol.replace(':', '_')}_{timestamp}.mp3"
                
                success = await voice.save_to_file(analysis, voice_config, filename)
                
                if success:
                    print(f"🔊 Audio saved: {filename}")
                    
                    # Read and broadcast audio
                    with open(filename, 'rb') as f:
                        audio_bytes = f.read()
                    await manager.broadcast_bytes(audio_bytes)
                    
        except Exception as e:
            print(f"Intelligence error: {e}")
            
        alert_queue.task_done()


async def mock_tick_generator():
    """
    Generates mock ticks for testing when Kite is not available.
    Simulates NIFTY 50 stocks with random price movements.
    """
    import random
    
    stocks = {
        "RELIANCE": 2500.00,
        "TCS": 3800.00,
        "INFY": 1500.00,
        "HDFCBANK": 1600.00,
        "ICICIBANK": 1000.00,
    }
    
    print("Mock tick generator started (for testing without Kite API)...")
    
    while True:
        for symbol, base_price in stocks.items():
            # Random walk: -0.5% to +0.5%
            change = random.uniform(-0.005, 0.005)
            new_price = base_price * (1 + change)
            stocks[symbol] = new_price
            
            tick = {
                "symbol": f"NSE:{symbol}",
                "ltp": round(new_price, 2),
                "volume": random.randint(10000, 100000),
            }
            
            try:
                tick_queue.put_nowait(tick)
            except asyncio.QueueFull:
                pass  # Drop tick if queue full
                
        await asyncio.sleep(0.5)  # 2 ticks per second per stock


# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: start background workers on startup."""
    
    tasks = []
    
    # Data source priority: Kite Connect > Yahoo Finance > Mock
    if settings.KITE_API_KEY and settings.KITE_ACCESS_TOKEN:
        # Production: Use real Kite Connect (requires trading account)
        kite_ingestor = KiteTickerIngestor(
            settings.KITE_API_KEY,
            settings.KITE_ACCESS_TOKEN,
            tick_queue
        )
        tasks.append(asyncio.create_task(kite_ingestor.connect()))
        print("🔴 Using Kite Connect for LIVE data...")
    else:
        # Free tier: Use Yahoo Finance (delayed ~15 min, no account needed)
        yahoo_ingestor = YahooFinanceIngestor(tick_queue)
        tasks.append(asyncio.create_task(yahoo_ingestor.connect()))
        print("📊 Using Yahoo Finance for FREE NSE data (15-min delay)")
    
    # Add Finage for US/UK markets (if API key configured)
    if settings.FINAGE_API_KEY:
        finage_ingestor = FinageIngestor(
            api_key=settings.FINAGE_API_KEY,
            tick_queue=tick_queue
        )
        tasks.append(asyncio.create_task(finage_ingestor.connect()))
        print("🌍 Using Finage for US/UK real-time data")
    
    # Start processing worker
    tasks.append(asyncio.create_task(processing_worker()))
    
    # Start intelligence worker (Gemini + ElevenLabs)
    tasks.append(asyncio.create_task(intelligence_worker()))
    
    print("=" * 50)
    print("PulseTrade AI Started!")
    print(f"Queue sizes: tick={tick_queue.maxsize}, alert={alert_queue.maxsize}")
    print(f"Gemini API: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    print(f"ElevenLabs API: {'✅' if settings.ELEVENLABS_API_KEY else '❌'}")
    print("=" * 50)
    
    yield
    
    # Cleanup on shutdown
    print("Shutting down workers...")
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="PulseTrade AI",
    description="High-frequency multimodal trading assistant",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware - Required for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PulseTrade AI is running", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check with queue status."""
    return {
        "status": "ok",
        "tick_queue_size": tick_queue.qsize(),
        "alert_queue_size": alert_queue.qsize(),
        "connected_clients": len(manager.active_connections),
    }


@app.websocket("/ws/market")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time market data."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Handle client commands (e.g., subscribe to symbols)
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# Run with: uvicorn app.main:app --reload
# ============================================================================
