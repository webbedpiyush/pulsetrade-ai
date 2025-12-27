# 🚀 PulseTrade AI - Hackathon Project Reference

**Real-time AI-powered trading assistant with voice alerts**

A comprehensive reference documentation for building similar hackathon projects featuring real-time data streaming, AI analysis, and voice synthesis.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Hackathon Implementation Plan](#-hackathon-implementation-plan)
3. [Architecture](#-architecture)
4. [Tech Stack](#-tech-stack)
5. [Folder Structure](#-folder-structure)
6. [Implementation Breakdown](#-implementation-breakdown)
7. [Code Structure Rules](#-code-structure-rules)
8. [Key Learnings](#-key-learnings)
9. [Quick Start](#-quick-start)
10. [Environment Variables](#-environment-variables)
11. [API Reference](#-api-reference)

---

## 🎯 Project Overview

### What It Does
PulseTrade AI monitors global stock markets (India NSE, US NYSE/NASDAQ, UK LSE) in real-time, detects technical breakouts, and announces them using AI-generated voice alerts.

### Core Features
| Feature | Description |
|---------|-------------|
| **Multi-Market Data** | Yahoo Finance integration for NIFTY 50, S&P 500, FTSE 100 |
| **Technical Analysis** | SMA, VWAP, Volatility, RSI, Breakout detection |
| **AI Analysis** | Gemini 2.5 Flash generates market insights |
| **Voice Alerts** | ElevenLabs TTS announces breakouts in real-time |
| **Live Dashboard** | WebSocket-powered UI with TradingView charts |
| **Portfolio Management** | Clerk auth + Prisma database for user portfolios |
| **LLM Observability** | Datadog APM for Gemini telemetry and monitoring |

---

## 🏆 Hackathon Implementation Plan

**Target Challenges:** ElevenLabs + Datadog (dual submission)

### Requirements Checklist

#### ElevenLabs Challenge
- [x] ElevenLabs for voice synthesis (Flash v2.5)
- [x] Google Cloud AI (Gemini 2.5 Flash)
- [x] Voice-driven interface with localized personas
- [ ] Upgrade to WebSocket streaming (~75ms latency)
- [ ] Deploy to hosted URL (Google Cloud Run)

#### Datadog Challenge
- [ ] Install `ddtrace` and `datadog` Python packages
- [ ] Stream Gemini LLM telemetry (latency, tokens, errors)
- [ ] Define detection rules (slow response >2s, errors)
- [ ] Create observability dashboard
- [ ] Set up alerts when rules trigger

### Current Status

| Component | Status |
|-----------|--------|
| Market Data (Yahoo Finance - India) | ✅ Done |
| Market Data (US/UK stocks) | ✅ Done |
| Gemini 2.5 Flash integration | ✅ Done |
| ElevenLabs voice synthesis | ✅ Done |
| Technical indicators (SMA, VWAP, breakout) | ✅ Done |
| Redis state management | ✅ Done |
| React dashboard with WebSocket | ✅ Done |
| Datadog observability | ❌ TODO |
| Google Cloud deployment | ❌ TODO |

### Implementation Phases

#### Phase 1: Multi-Market Yahoo Finance ✅
Extend Yahoo ingestor to fetch US + UK stocks alongside NIFTY 50.

**[MODIFY] `yahoo.py`**
- Add US_SYMBOLS list (AAPL, MSFT, GOOGL, etc.)
- Add UK_SYMBOLS list with `.L` suffix (SHEL.L, BP.L, etc.)
- Normalize symbols to `NYSE:AAPL`, `LSE:SHEL` format
- Handle GBX→GBP conversion for UK stocks

---

#### Phase 2: Datadog LLM Observability (1-2 days)

**[NEW] `observability.py`**
- Initialize Datadog tracer with `ddtrace`
- Create custom metrics:
  - `pulsetrade.gemini.latency` - Time to first token
  - `pulsetrade.gemini.tokens` - Output token count
  - `pulsetrade.voice.latency` - Time to audio start
  - `pulsetrade.alert.count` - Alerts triggered per market

**[MODIFY] `gemini_live.py`**
- Wrap generation calls with `@tracer.wrap`
- Log token usage and latency to Datadog

**[NEW] Datadog Dashboard**
- LLM response latency (p50, p95, p99)
- Error rate by market
- Alerts per hour
- Voice generation latency

**Detection Rules**

| Rule | Condition | Action |
|------|-----------|--------|
| Slow LLM Response | Latency > 2000ms | Create incident |
| High Error Rate | Errors > 5/min | Alert on-call |
| Voice Synthesis Failure | ElevenLabs 4xx/5xx | Log warning |

---

#### Phase 3: Voice Experience Polish (1 day)

**[MODIFY] `synthesizer.py`**
- Upgrade `synthesize_stream` to true WebSocket streaming
- Target ~75ms time-to-first-audio

**[MODIFY] `AudioStreamPlayer.tsx`**
- Add 250ms jitter buffer for smooth playback

---

#### Phase 4: Deployment (1 day)

**Google Cloud Run**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/pulsetrade-backend

# Deploy backend
gcloud run deploy pulsetrade-backend \
  --image gcr.io/PROJECT_ID/pulsetrade-backend \
  --platform managed \
  --region us-central1

# Deploy frontend (Vercel or Cloud Run)
```

### Architecture with Datadog

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PulseTrade AI + Datadog                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐   │
│  │ Yahoo       │───▶│ asyncio     │───▶│ Indicator   │───▶│ Breakout?       │   │
│  │ Finance     │    │ Queue       │    │ Engine      │    │                 │   │
│  │ India/US/UK │    └─────────────┘    └─────────────┘    └────────┬────────┘   │
│  └─────────────┘                                                   │ Yes        │
│                                                                    ▼            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         AI + Voice Pipeline                              │   │
│  │  ┌──────────────────┐         ┌──────────────────┐                      │   │
│  │  │  Gemini 2.5      │────────▶│  ElevenLabs      │                      │   │
│  │  │  Flash           │         │  Flash v2.5      │                      │   │
│  │  └────────┬─────────┘         └────────┬─────────┘                      │   │
│  │           │ traces                     │ metrics                         │   │
│  │           ▼                            ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────┐                   │   │
│  │  │              Datadog APM + Metrics                │                   │   │
│  │  │  • LLM latency (p50, p95, p99)                   │                   │   │
│  │  │  • Token usage per request                        │                   │   │
│  │  │  • Voice synthesis latency                        │                   │   │
│  │  │  • Error tracking by market                       │                   │   │
│  │  └────────────────────┬─────────────────────────────┘                   │   │
│  └───────────────────────┼─────────────────────────────────────────────────┘   │
│                          ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Datadog Dashboard                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ LLM Latency │  │ Error Rate  │  │ Alerts/Hour │  │ Incidents   │     │   │
│  │  │   Graphs    │  │   by Mkt    │  │   Counter   │  │   Panel     │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                          │                                                      │
│                          ▼                                                      │
│  ┌─────────────┐    ┌─────────────┐                                            │
│  │ WebSocket   │───▶│ React       │                                            │
│  │ /ws         │    │ Dashboard   │                                            │
│  └─────────────┘    └─────────────┘                                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Datadog Testing

```bash
# Set environment variables
export DD_API_KEY=your_datadog_api_key
export DD_SITE=datadoghq.com

# Run backend with ddtrace
ddtrace-run uvicorn app.main:app --reload

# Trigger market alerts and verify:
# 1. Traces appear in Datadog APM
# 2. Custom metrics in Metrics Explorer
# 3. Detection rules trigger correctly
```

### Demo Video Outline (3 min)

| Time | Content |
|------|---------|
| 0:00 - 0:30 | **Problem:** Information overload in trading |
| 0:30 - 1:30 | **Demo:** Real-time voice alerts across markets |
| 1:30 - 2:30 | **Datadog:** Show LLM observability dashboard |
| 2:30 - 3:00 | **Architecture:** Gemini + ElevenLabs + Datadog |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PulseTrade AI                                   │
├──────────────────────────────┬──────────────────────────────────────────────┤
│         FRONTEND             │                  BACKEND                      │
│  (Next.js 16 + ShadCN UI)    │           (FastAPI + Python)                 │
├──────────────────────────────┼──────────────────────────────────────────────┤
│                              │                                               │
│  ┌──────────────────────┐    │    ┌─────────────────────────────────────┐   │
│  │   Dashboard Page     │◄───┼────┤     WebSocket /ws Endpoint          │   │
│  │   - PriceChart       │    │    │     (JSON + Binary Audio)           │   │
│  │   - TickerGrid       │    │    └─────────────┬───────────────────────┘   │
│  │   - AlertFeed        │    │                  │                           │
│  │   - PortfolioManager │    │    ┌─────────────▼───────────────────────┐   │
│  │   - AudioStreamPlayer│    │    │      Connection Manager             │   │
│  └──────────────────────┘    │    │      (Broadcast to all clients)     │   │
│                              │    └─────────────┬───────────────────────┘   │
│  ┌──────────────────────┐    │                  │                           │
│  │   Zustand Store      │    │    ┌─────────────▼───────────────────────┐   │
│  │   - ticks{}          │    │    │      Background Workers              │   │
│  │   - alerts[]         │    │    ├─────────────────────────────────────┤   │
│  │   - priceHistory{}   │    │    │  Worker 1: Processing               │   │
│  │   - selectedSymbol   │    │    │    └→ IndicatorEngine               │   │
│  │   - latestAnalysis   │    │    │    └→ Breakout Detection            │   │
│  └──────────────────────┘    │    │    └→ Alert Queue                   │   │
│                              │    ├─────────────────────────────────────┤   │
│  ┌──────────────────────┐    │    │  Worker 2: Intelligence             │   │
│  │   Clerk Auth         │    │    │    └→ Gemini AI Analysis            │   │
│  │   (Sign In/Up)       │    │    │    └→ ElevenLabs Voice              │   │
│  └──────────────────────┘    │    │    └→ Audio Broadcast               │   │
│                              │    └─────────────┬───────────────────────┘   │
│  ┌──────────────────────┐    │                  │                           │
│  │   API Routes         │    │    ┌─────────────▼───────────────────────┐   │
│  │   /api/portfolio     │    │    │      Data Ingestors                 │   │
│  │   /api/portfolio/[id]│    │    │    └→ Yahoo Finance (Polling)       │   │
│  └──────────────────────┘    │    │    └→ Kite Connect (WebSocket)      │   │
│                              │    │    └→ Finage (Streaming)            │   │
└──────────────────────────────┴────┴─────────────────────────────────────────┘
```

### Data Flow
1. **Ingestor** polls Yahoo Finance every 5 seconds for all tracked symbols
2. **Tick Queue** receives raw price/volume data
3. **Processing Worker** calculates indicators, detects breakouts
4. **Alert Queue** receives breakout events
5. **Intelligence Worker** sends to Gemini AI, then ElevenLabs
6. **Connection Manager** broadcasts JSON + audio to all WebSocket clients
7. **Frontend** updates Zustand store, renders UI, plays audio

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **FastAPI** | Web framework | Async-first, WebSocket support, auto-docs |
| **asyncio** | Async/await | Non-blocking I/O for real-time |
| **yfinance** | Market data | Free, reliable, global markets |
| **Redis** | State/caching | Low-latency, pub/sub capabilities |
| **google-genai** | AI analysis | Gemini 2.5 Flash - fast, multimodal |
| **httpx** | HTTP client | Async support, streaming |
| **orjson** | JSON parsing | 3-10x faster than stdlib json |
| **Pydantic** | Settings/validation | Type-safe config, env parsing |

### Frontend
| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Next.js 16** | React framework | App router, API routes, RSC |
| **TypeScript** | Type safety | Catch errors at compile time |
| **ShadCN/UI** | Component library | Customizable, accessible, modern |
| **Tailwind CSS 4** | Styling | Utility-first, dark mode |
| **Zustand** | State management | Simple, fast, no boilerplate |
| **Framer Motion** | Animations | Smooth, declarative animations |
| **Clerk** | Authentication | Pre-built auth, webhooks, user management |
| **Prisma** | Database ORM | Type-safe queries, migrations |
| **TradingView Charts** | Price charts | Professional, feature-rich |

---

## 📁 Folder Structure

```
stock-alert/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, WebSocket, workers
│   │   ├── config.py               # Pydantic settings from .env
│   │   │
│   │   ├── ingestors/              # Data source adapters
│   │   │   ├── __init__.py
│   │   │   ├── yahoo.py            # Yahoo Finance (polling)
│   │   │   ├── kite.py             # Zerodha Kite (WebSocket)
│   │   │   └── finage.py           # Finage API (streaming)
│   │   │
│   │   ├── processors/             # Business logic
│   │   │   ├── __init__.py
│   │   │   └── indicators.py       # SMA, VWAP, breakout detection
│   │   │
│   │   ├── intelligence/           # AI integration
│   │   │   ├── __init__.py
│   │   │   ├── gemini_live.py      # Gemini 2.5 Flash client
│   │   │   └── prompts.py          # System prompts (persona)
│   │   │
│   │   ├── voice/                  # TTS integration
│   │   │   ├── __init__.py
│   │   │   ├── synthesizer.py      # ElevenLabs client
│   │   │   └── voices.py           # Voice configurations
│   │   │
│   │   ├── state/                  # Caching layer
│   │   │   ├── __init__.py
│   │   │   └── redis_client.py     # Redis operations
│   │   │
│   │   └── models/                 # Data models
│   │       ├── __init__.py
│   │       └── tick.py             # Tick, Alert schemas
│   │
│   ├── tests/                      # Pytest tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx            # Landing page
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── globals.css         # Tailwind + theme
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx        # Main dashboard
│   │   │   ├── api/                # API routes
│   │   │   │   └── portfolio/      # Portfolio CRUD
│   │   │   ├── sign-in/            # Clerk auth pages
│   │   │   └── sign-up/
│   │   │
│   │   ├── components/             # React components
│   │   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   │   ├── StatCard.tsx        # Metric cards
│   │   │   ├── PriceChart.tsx      # TradingView chart
│   │   │   ├── TickerGrid.tsx      # Stock grid
│   │   │   ├── AlertFeed.tsx       # AI alerts feed
│   │   │   ├── PortfolioManager.tsx # Portfolio CRUD
│   │   │   ├── AudioStreamPlayer.tsx # Audio playback
│   │   │   └── ui/                 # ShadCN components
│   │   │
│   │   ├── hooks/                  # Custom hooks
│   │   │   └── useMarketWebSocket.ts # WebSocket hook
│   │   │
│   │   ├── stores/                 # Zustand stores
│   │   │   └── marketStore.ts      # Market state
│   │   │
│   │   └── lib/                    # Utilities
│   │       ├── utils.ts            # cn() helper
│   │       └── prisma.ts           # Prisma client
│   │
│   ├── prisma/
│   │   └── schema.prisma           # Database schema
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml              # Full stack deployment
├── README.md                       # This file
└── .gitignore
```

---

## 🔧 Implementation Breakdown

### 1. Data Ingestion Layer

**File:** `backend/app/ingestors/yahoo.py`

```python
class YahooFinanceIngestor:
    """
    Polls Yahoo Finance for real-time prices.
    
    Key patterns:
    - Async polling loop with configurable interval
    - Dynamic symbol fetching (NSE from API, S&P/FTSE from Wikipedia)
    - Symbol normalization (RELIANCE.NS → NSE:RELIANCE)
    - Batch requests with retry logic for reliability
    """
    
    async def connect(self):
        while self.running:
            await self._fetch_batch_prices(symbols)
            await asyncio.sleep(self.poll_interval)
```

**Key Learnings:**
- Use smaller batches (50-100 symbols) to avoid API timeouts
- Normalize symbols to consistent format (`MARKET:SYMBOL`)
- Wikipedia tables are reliable for index constituents

---

### 2. Technical Indicators

**File:** `backend/app/processors/indicators.py`

```python
class IndicatorEngine:
    """
    Sliding window calculations for real-time indicators.
    
    Patterns:
    - collections.deque for O(1) append/pop
    - numpy for vectorized calculations
    - Breakout = price deviation > 2 * volatility from SMA
    """
    
    def update(self, symbol, price, volume) -> TechnicalSnapshot:
        # Append to sliding window
        self.price_windows[symbol].append(price)
        
        # Calculate SMA, VWAP, volatility
        prices = np.array(self.price_windows[symbol])
        sma_5 = np.mean(prices[-30:])
        
        # Breakout detection
        is_breakout = deviation > 2 * volatility
```

---

### 3. AI Integration

**File:** `backend/app/intelligence/gemini_live.py`

```python
class GeminiLiveClient:
    """
    Gemini 2.5 Flash for market analysis.
    
    Patterns:
    - System prompt for persona (Victor Sterling)
    - Streaming for low latency
    - Async for non-blocking
    """
    
    async def generate_stream(self, prompt):
        response = self.client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=256,
            )
        )
```

**File:** `backend/app/intelligence/prompts.py`
```python
PULSETRADE_SYSTEM_PROMPT = """
You are Victor Sterling, a seasoned Wall Street analyst...
Keep responses under 30 words for TTS brevity.
"""
```

---

### 4. Voice Synthesis

**File:** `backend/app/voice/synthesizer.py`

```python
class ElevenLabsSynthesizer:
    """
    ElevenLabs Flash v2.5 TTS.
    
    Patterns:
    - Text normalization (₹ → Rupees, SMA → moving average)
    - REST API for reliability (WebSocket for lower latency)
    - Sentence-boundary chunking for streaming
    """
    
    def _normalize_text(self, text):
        replacements = {
            "₹": "Rupees ",
            "200 DMA": "two hundred day moving average",
            "%": " percent",
        }
```

---

### 5. WebSocket Broadcasting

**File:** `backend/app/main.py`

```python
class ConnectionManager:
    """
    Manages WebSocket connections.
    
    Patterns:
    - List of active connections
    - broadcast_json() for tick/alert data
    - broadcast_bytes() for audio streaming
    - Error handling with disconnect on failure
    """
    
    async def broadcast_json(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                await self.disconnect(connection)
```

---

### 6. Frontend State Management

**File:** `frontend/src/stores/marketStore.ts`

```typescript
interface MarketStore {
  connected: boolean;
  ticks: Record<string, Tick>;
  alerts: Alert[];
  priceHistory: Record<string, PricePoint[]>;
  selectedSymbol: string;
  latestAnalysis: Analysis | null;
  
  // Actions
  setConnected: (connected: boolean) => void;
  updateTick: (tick: Tick) => void;
  addAlert: (alert: Alert) => void;
}

export const useMarketStore = create<MarketStore>((set) => ({
  // Zustand implementation
}));
```

---

### 7. WebSocket Hook

**File:** `frontend/src/hooks/useMarketWebSocket.ts`

```typescript
export function useMarketWebSocket() {
  const store = useMarketStore();
  
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onmessage = (event) => {
      if (event.data instanceof Blob) {
        // Audio data → play
        playAudio(event.data);
      } else {
        // JSON data → update store
        const data = JSON.parse(event.data);
        if (data.type === "tick") store.updateTick(data);
        if (data.type === "alert") store.addAlert(data);
      }
    };
    
    return () => ws.close();
  }, []);
}
```

---

## 📐 Code Structure Rules

### Backend Rules

1. **Single Responsibility**
   - One file = one concern (ingestor, processor, client)
   - Classes do one thing well

2. **Async Everything**
   - All I/O operations must be `async`
   - Use `asyncio.Queue` for worker communication
   - Never block the event loop

3. **Configuration**
   - All secrets in `.env`
   - Use Pydantic `Settings` class
   - Never hardcode API keys

4. **Error Handling**
   ```python
   try:
       result = await api_call()
   except Exception as e:
       logger.error(f"API error: {e}")
       return fallback_value
   ```

5. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Tick received: %s", symbol)
   ```

### Frontend Rules

1. **Component Structure**
   ```typescript
   // Good: Props interface → Component → Export
   interface Props {
     title: string;
   }
   
   export function MyComponent({ title }: Props) {
     return <div>{title}</div>;
   }
   ```

2. **State Management**
   - Global state → Zustand store
   - Component state → `useState`
   - Server state → `useEffect` + fetch

3. **Styling**
   - Use Tailwind utilities
   - Extract common patterns to `globals.css`
   - Use `cn()` for conditional classes

4. **API Routes**
   ```typescript
   // app/api/resource/route.ts
   export async function GET() {
     const data = await prisma.resource.findMany();
     return Response.json(data);
   }
   ```

5. **Error Boundaries**
   - Wrap pages in error boundaries
   - Show user-friendly error states

---

## 💡 Key Learnings

### Technical Learnings

1. **WebSocket Binary Streaming**
   - Check `event.data instanceof Blob` for binary
   - Use `URL.createObjectURL(blob)` for audio playback
   - Clean up old object URLs to prevent memory leaks

2. **Yahoo Finance Quirks**
   - `.NS` suffix for NSE stocks
   - `.L` suffix for LSE stocks
   - Batch requests timeout at ~100 symbols

3. **Gemini 2.5 Flash**
   - Use `google-genai` SDK (not deprecated `google-generativeai`)
   - System instructions via `GenerateContentConfig`
   - Streaming is significantly faster for TTS pipeline

4. **ElevenLabs Optimization**
   - Flash v2.5 model for lowest latency
   - Normalize text before synthesis (₹, %, acronyms)
   - Buffer text to sentence boundaries for natural speech

5. **Next.js 16 Patterns**
   - Server components by default
   - "use client" for interactivity
   - API routes in `app/api/` folder

### Architecture Learnings

1. **Queue-Based Decoupling**
   - Separate ingest → process → broadcast
   - Allows independent scaling
   - Prevents backpressure issues

2. **WebSocket vs REST**
   - WebSocket for real-time data streaming
   - REST for CRUD operations (portfolios)
   - Both can coexist on same FastAPI app

3. **State Management Split**
   - Zustand for client-side UI state
   - Backend queues for processing state
   - Redis for cross-instance caching

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Redis (optional, for caching)

### 1. Clone Repository
```bash
git clone <repo-url>
cd stock-alert
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with Clerk keys
```

### 4. Run Services
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Redis (optional)
redis-server
```

### 5. Open Dashboard
Visit http://localhost:3000

---

## 🔐 Environment Variables

### Backend `.env`
```env
# Required
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Optional - Live data sources
KITE_API_KEY=
KITE_ACCESS_TOKEN=
FINAGE_API_KEY=

# Voice configuration
VOICE_ID_INDIA=21m00Tcm4TlvDq8ikWAM
VOICE_ID_UK=pNInz6obpgDQGcFmaJgB
VOICE_ID_US=ErXwobaYiN019PkySvjV

# Redis
REDIS_URL=redis://localhost:6379
```

### Frontend `.env.local`
```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...

# API endpoints
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Prisma
DATABASE_URL=file:./dev.db
```

---

## 📡 API Reference

### WebSocket `/ws`

**Message Types (JSON):**
```typescript
// Tick update
{ type: "tick", symbol: "NSE:RELIANCE", price: 2450.50, volume: 1234567 }

// Breakout alert
{ type: "alert", symbol: "NSE:TCS", direction: "UP", price: 3850.25, time: "..." }

// AI analysis
{ type: "analysis", symbol: "NSE:INFY", text: "Bullish momentum detected..." }
```

**Binary Messages:**
- MP3 audio bytes for voice alerts
- Check `event.data instanceof Blob`

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Health check |
| `GET /health` | GET | Detailed status |
| `GET /api/portfolio` | GET | List portfolios |
| `POST /api/portfolio` | POST | Create portfolio |
| `GET /api/portfolio/:id` | GET | Get portfolio |
| `DELETE /api/portfolio/:id` | DELETE | Delete portfolio |
| `POST /api/portfolio/:id/stocks` | POST | Add stock |
| `DELETE /api/portfolio/:id/stocks` | DELETE | Remove stock |

---

## 📄 License

MIT

---

## 🙏 Credits

- [Yahoo Finance](https://finance.yahoo.com/) - Market data
- [Google Gemini](https://ai.google.dev/) - AI analysis
- [ElevenLabs](https://elevenlabs.io/) - Voice synthesis
- [ShadCN/UI](https://ui.shadcn.com/) - Component library
- [TradingView](https://www.tradingview.com/) - Charts
