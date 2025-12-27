"""
PulseTrade AI: Crypto Edition - FastAPI Backend

Real-time crypto streaming with Binance, Kafka, Gemini, and ElevenLabs.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.services.ingestor import get_ingestor


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
    
    # Start Binance Ingestor
    ingestor = get_ingestor()
    ingestor_task = asyncio.create_task(ingestor.start())
    
    # TODO: Start Analyzer (Phase 2)
    # TODO: Start Voice Service (Phase 3)
    
    yield
    
    # Shutdown
    print("[Shutdown] Stopping services...")
    ingestor.stop()
    ingestor_task.cancel()
    try:
        await ingestor_task
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
    return {
        "status": "healthy",
        "ingestor": {
            "running": ingestor.running,
            "messages_processed": ingestor.message_count,
        },
        "websocket_clients": len(manager.active_connections),
    }


@app.post("/debug/trigger")
async def debug_trigger():
    """
    Force trigger an alert for demo purposes.
    Injects a fake $100k BTC event.
    """
    # TODO: Implement in Phase 3
    return {"status": "triggered", "message": "Demo alert triggered"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Handle ping/pong or client commands if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =============================================================================
# Run with: uvicorn app.main:app --reload
# =============================================================================
