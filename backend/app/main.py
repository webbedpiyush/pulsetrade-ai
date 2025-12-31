"""
PulseTrade AI: Crypto Edition - FastAPI Backend

Real-time crypto streaming with Binance, Kafka, Gemini, and ElevenLabs.
"""
import asyncio
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.services.ingestor import get_ingestor
from app.services.analyzer import get_analyzer
from app.services.voice import get_voice_service
from app.models.trade import AlertEvent


# =============================================================================
# WebSocket Connection Manager
# =============================================================================

class ConnectionManager:
    """Manages WebSocket connections to frontend clients."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast_json(self, data: dict):
        """Broadcast JSON to all clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)
            
    async def broadcast_bytes(self, data: bytes):
        """Broadcast binary (audio) to all clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_bytes(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background workers on startup."""
    print("[Startup] Starting PulseTrade AI: Crypto Edition")
    
    # Get services
    ingestor = get_ingestor()
    analyzer = get_analyzer()
    voice = get_voice_service()
    
    # Wire up callbacks
    async def on_alert(alert: AlertEvent):
        """Broadcast alert to frontend."""
        await manager.broadcast_json({
            "type": "alert",
            "data": {
                "symbol": alert.symbol,
                "price": alert.price,
                "triggerType": alert.trigger_type,
                "triggerValue": alert.trigger_value,
                "message": alert.message,
                "time": alert.time,
            }
        })
    
    async def on_analysis(symbol: str, text: str):
        """Generate voice and broadcast."""
        # Broadcast text first
        await manager.broadcast_json({
            "type": "analysis",
            "data": {
                "symbol": symbol,
                "text": text,
                "time": int(time.time() * 1000),
            }
        })
        
        # Generate and broadcast audio (voice.speak returns the audio bytes)
        audio = await voice.speak(text)
        if audio:
            await manager.broadcast_bytes(audio)
    
    async def on_trade(trade):
        """Broadcast trade to frontend."""
        await manager.broadcast_json({
            "type": "trade",
            "data": {
                "symbol": trade.symbol,
                "price": trade.price,
                "volume": trade.volume,
                "time": trade.time,
            }
        })
    
    # Set callbacks (NOTE: we don't set voice.on_audio_chunk since we broadcast
    # audio directly in on_analysis after voice.speak() returns)
    ingestor.on_trade = on_trade
    analyzer.on_alert = on_alert
    analyzer.on_analysis = on_analysis
    
    # Save money: Only run AI if someone is listening
    analyzer.connection_check_callback = lambda: len(manager.active_connections) > 0
    
    # Start background tasks
    ingestor_task = asyncio.create_task(ingestor.start())
    analyzer_task = asyncio.create_task(analyzer.start())
    
    yield
    
    # Shutdown
    print("[Shutdown] Stopping services...")
    ingestor.stop()
    analyzer.stop()
    ingestor_task.cancel()
    analyzer_task.cancel()
    
    for task in [ingestor_task, analyzer_task]:
        try:
            await task
        except asyncio.CancelledError:
            pass


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="PulseTrade AI: Crypto Edition",
    description="Real-time crypto streaming with voice alerts",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {"service": "PulseTrade AI: Crypto Edition", "status": "running"}


@app.get("/health")
async def health():
    """Health check with status."""
    ingestor = get_ingestor()
    analyzer = get_analyzer()
    return {
        "status": "healthy",
        "ingestor": {
            "running": ingestor.running,
            "messages_processed": ingestor.message_count,
        },
        "analyzer": {
            "running": analyzer.running,
            "trades_processed": analyzer.trades_processed,
            "alerts_triggered": analyzer.alerts_triggered,
        },
        "websocket_clients": len(manager.active_connections),
    }


@app.post("/debug/trigger")
async def debug_trigger():
    """
    Force trigger an alert for demo purposes.
    Injects a fake BTC pump event.
    """
    analyzer = get_analyzer()
    voice = get_voice_service()
    
    # Create fake alert
    fake_alert = AlertEvent(
        symbol="BTCUSDT",
        price=100000.0,
        trigger_type="PRICE_LEVEL",
        trigger_value=100000.0,
        message="Bitcoin just hit $100,000! Historic moment!",
        time=int(time.time() * 1000),
    )
    
    # Broadcast alert
    await manager.broadcast_json({
        "type": "alert",
        "data": {
            "symbol": fake_alert.symbol,
            "price": fake_alert.price,
            "triggerType": fake_alert.trigger_type,
            "triggerValue": fake_alert.trigger_value,
            "message": fake_alert.message,
            "time": fake_alert.time,
        }
    })
    
    # Generate AI response
    analysis_text = "Bitcoin just smashed through one hundred thousand dollars! This is absolutely massive - a historic psychological barrier broken. Is this the start of a new bull run or the ultimate trap? Stay alert!"
    
    # Broadcast analysis
    await manager.broadcast_json({
        "type": "analysis",
        "data": {
            "symbol": "BTCUSDT",
            "text": analysis_text,
            "time": int(time.time() * 1000),
        }
    })
    
    # Speak it
    audio = await voice.speak(analysis_text)
    if audio:
        await manager.broadcast_bytes(audio)
    
    return {"status": "triggered", "message": fake_alert.message}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data."""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages with a timeout to send heartbeats
            try:
                # Wait 10 seconds for a message
                data = await asyncio.wait_for(websocket.receive_text(), timeout=10)
                # Handle client messages if needed
            except asyncio.TimeoutError:
                # No data from client? Send a "ping" to keep connection alive
                # (The client doesn't strictly need to respond if it's just a keep-alive)
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =============================================================================
# Run with: ddtrace-run uvicorn app.main:app --reload
# =============================================================================
