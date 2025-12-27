# 🚀 PulseTrade AI: Crypto Edition - Implementation Rules

> **Strategic Pivot:** Moving from Stock Markets (Yahoo Finance polling) to Crypto (Binance WebSocket streaming)

This document contains all rules, patterns, and implementation details for the crypto revamp.

---

## 📋 Table of Contents

1. [Why Crypto?](#-why-crypto)
2. [Target Hackathon Tracks](#-target-hackathon-tracks)
3. [Architecture](#-architecture)
4. [Docker Compose Setup](#-docker-compose-setup)
5. [Confluent Cloud Setup](#-confluent-cloud-setup)
6. [Folder Structure](#-folder-structure)
7. [Implementation Phases](#-implementation-phases)
8. [Frontend Layout Code](#-frontend-layout-code)
9. [Code Patterns](#-code-patterns)
10. [Voice AI Trigger Logic](#-voice-ai-trigger-logic)
11. [UI Component Breakdown](#-ui-component-breakdown)
12. [Environment Variables](#-environment-variables)
13. [Execution Strategy](#-execution-strategy)

---

## 🎯 Why Crypto?

| Problem with Stocks | Crypto Solution |
|---------------------|-----------------|
| Market hours (9:15 AM - 3:30 PM IST) | **24/7 trading** - demo anytime |
| Yahoo Finance polling (5s delay) | **Binance WebSocket** - millisecond updates |
| API rate limits | **Free & unlimited** public streams |
| ~50 symbols (NIFTY 50) | **1000+ events/second** (perfect for Confluent) |

---

## 🏆 Target Hackathon Tracks

| Track | Integration | Proof |
|-------|-------------|-------|
| **Confluent (Data in Motion)** | Kafka for trade streaming | Live Trade Stream panel showing JSON events |
| **Datadog (Observability)** | APM traces on Gemini/Voice | Dashboard showing latency percentiles |
| **ElevenLabs (Voice)** | Turbo v2.5 streaming | AI Pulse panel with voice feedback |
| **Google Cloud (AI)** | Gemini 1.5 Flash analysis | Text transcript in UI |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     PulseTrade AI: Crypto Edition                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  INGESTION LAYER (The Firehose)                                                  │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────────┐   │
│  │  Binance         │─────▶│  Python          │─────▶│  Confluent Cloud     │   │
│  │  WebSocket       │      │  Ingestor        │      │  Kafka               │   │
│  │  (BTC/ETH/SOL)   │      │  (Producer)      │      │  Topic: crypto-trades│   │
│  └──────────────────┘      └──────────────────┘      └──────────┬───────────┘   │
│                                                                  │               │
│  PROCESSING LAYER (The Brain)                                   │               │
│  ┌──────────────────────────────────────────────────────────────▼───────────┐   │
│  │  Consumer Service                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐   │   │
│  │  │ Technical       │───▶│ Breakout        │───▶│ Gemini 1.5 Flash    │   │   │
│  │  │ Analysis Engine │    │ Router          │    │ (only on triggers)  │   │   │
│  │  │ RSI/MACD/Volume │    │ (Yes/No)        │    │                     │   │   │
│  │  └─────────────────┘    └────────┬────────┘    └──────────┬──────────┘   │   │
│  │                                  │ No                     │ Text         │   │
│  │                                  ▼                        ▼              │   │
│  │                             [Ignore]              ┌──────────────────┐   │   │
│  │                                                   │ ElevenLabs       │   │   │
│  │                                                   │ Turbo v2.5       │   │   │
│  └───────────────────────────────────────────────────┴──────────┬───────┘   │   │
│                                                                  │               │
│  INTERACTION LAYER (The Voice)                                  │               │
│  ┌──────────────────────────────────────────────────────────────▼───────────┐   │
│  │  FastAPI WebSocket Manager ──────▶ React Client (Audio + JSON)           │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  OBSERVABILITY (The Supervisor)                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │  Datadog Agent ◀── Traces from: Kafka Producer, Gemini, ElevenLabs       │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Binance WebSocket** pushes 10-50 trades/second for BTC/ETH/SOL
2. **Python Ingestor** produces events to Kafka topic
3. **Consumer Service** reads stream, calculates RSI/MACD
4. **Breakout Router** decides: trigger AI or ignore
5. **Gemini 1.5 Flash** generates 1-sentence insight
6. **ElevenLabs** converts text to audio stream
7. **WebSocket Manager** broadcasts to all React clients

---

## � Docker Compose Setup

This file spins up the entire stack including the **Datadog Agent** (required for Observability track).

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # Backend API (FastAPI)
  backend:
    build: ./backend
    container_name: pulsetrade-backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DD_SERVICE=pulsetrade-backend
      - DD_ENV=development
      - DD_AGENT_HOST=datadog-agent
      - DD_TRACE_AGENT_PORT=8126
    depends_on:
      - datadog-agent
    command: ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000

  # Frontend (Next.js)
  frontend:
    build: ./frontend
    container_name: pulsetrade-frontend
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
    depends_on:
      - backend

  # Datadog Agent (The Supervisor)
  datadog-agent:
    image: gcr.io/datadoghq/agent:7
    container_name: datadog-agent
    environment:
      - DD_API_KEY=${DD_API_KEY}
      - DD_SITE=datadoghq.com
      - DD_APM_ENABLED=true
      - DD_APM_NON_LOCAL_TRAFFIC=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
    ports:
      - "8126:8126"
```

### Running with Docker

```bash
# Set Datadog API key
export DD_API_KEY=your_datadog_api_key

# Build and run all services
docker-compose up --build

# View logs
docker-compose logs -f backend
```

---

## ☁️ Confluent Cloud Setup

> **Important:** If the topic isn't configured correctly, your producer will fail.

### Step-by-Step Setup

1. **Log in to Confluent Cloud**
   - Go to: https://confluent.cloud

2. **Create Cluster**
   - Type: **Basic** (Free tier)
   - Cloud: **Google Cloud**
   - Region: **US Central** (or closest to you)

3. **Create Topic**
   | Setting | Value |
   |---------|-------|
   | Topic Name | `crypto-trades` |
   | Partitions | `1` (keeps ordering simple) |
   | Retention | `1 day` (no need for history) |

4. **Create API Keys**
   - Go to **API Keys** → **Create Key** → **Global Access**
   - Save immediately to `.env`:
   ```env
   KAFKA_API_KEY=your_key_here
   KAFKA_API_SECRET=your_secret_here
   KAFKA_BOOTSTRAP_SERVERS=pkc-xxxxx.us-central1.gcp.confluent.cloud:9092
   ```

5. **Verify Connection**
   ```bash
   # Test with kafkacat (optional)
   kafkacat -b $KAFKA_BOOTSTRAP_SERVERS \
     -X security.protocol=SASL_SSL \
     -X sasl.mechanisms=PLAIN \
     -X sasl.username=$KAFKA_API_KEY \
     -X sasl.password=$KAFKA_API_SECRET \
     -L
   ```

---

## �📁 Folder Structure

```
pulsetrade-crypto/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI Entrypoint
│   │   │
│   │   ├── services/                   # Core Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── ingestor.py             # Binance WS → Confluent Producer
│   │   │   ├── analyzer.py             # Confluent Consumer → Gemini
│   │   │   └── voice.py                # ElevenLabs Streamer
│   │   │
│   │   ├── core/                       # Infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── kafka.py                # Kafka Config & Helpers
│   │   │   ├── datadog.py              # Observability Tracers
│   │   │   └── config.py               # Pydantic Settings
│   │   │
│   │   ├── indicators/                 # Technical Analysis
│   │   │   ├── __init__.py
│   │   │   ├── rsi.py                  # RSI Calculator
│   │   │   └── volume.py               # Volume Spike Detection
│   │   │
│   │   └── models/                     # Pydantic Models
│   │       ├── __init__.py
│   │       └── trade.py                # Trade, Alert Schemas
│   │
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── page.tsx                # Landing
│   │   │   ├── layout.tsx              # Root layout
│   │   │   ├── globals.css             # Tailwind + theme
│   │   │   └── dashboard/
│   │   │       └── page.tsx            # Main Dashboard
│   │   │
│   │   ├── components/                 # Feature Components
│   │   │   ├── LiveChart.tsx           # TradingView charts
│   │   │   ├── AIPulse.tsx             # Voice visualizer
│   │   │   ├── MarketOverview.tsx      # Multi-asset prices
│   │   │   ├── KafkaLogs.tsx           # JSON stream
│   │   │   └── ui/                     # ShadCN UI components
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── badge.tsx
│   │   │       └── scroll-area.tsx
│   │   │
│   │   ├── hooks/                      # Custom React Hooks
│   │   │   ├── useCryptoStream.ts      # WebSocket connection
│   │   │   └── useAudio.ts             # Audio playback
│   │   │
│   │   ├── providers/                  # React Context Providers
│   │   │   ├── WebSocketProvider.tsx   # WS connection context
│   │   │   └── AudioProvider.tsx       # Audio context
│   │   │
│   │   ├── services/                   # API & External Services
│   │   │   ├── api.ts                  # Backend REST calls
│   │   │   └── websocket.ts            # WS class wrapper
│   │   │
│   │   ├── stores/                     # Zustand State
│   │   │   └── cryptoStore.ts          # Market data store
│   │   │
│   │   ├── lib/                        # Utilities
│   │   │   ├── utils.ts                # cn() helper
│   │   │   └── constants.ts            # App constants
│   │   │
│   │   └── types/                      # TypeScript Types
│   │       └── index.ts                # Shared types
│   │
│   ├── components.json                 # ShadCN config
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
├── RULES.md                            # This file
└── README.md
```

### Frontend Code Organization Rules

1. **components/ui/** - ShadCN UI primitives (never modify directly)
2. **components/** - Feature components using ShadCN primitives
3. **hooks/** - Stateful logic extraction
4. **providers/** - React context for global state
5. **services/** - API clients and WebSocket wrappers
6. **stores/** - Zustand for client state
7. **lib/** - Pure utility functions
8. **types/** - Shared TypeScript interfaces

---

## 🔧 Implementation Phases

### Phase 1: The Firehose (Day 1)
**Goal:** Binance → Kafka working

```python
# backend/app/services/ingestor.py
import asyncio
import json
import websockets
from confluent_kafka import Producer
from ddtrace import tracer

conf = {
    'bootstrap.servers': 'pkc-xyz.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_API_KEY'),
    'sasl.password': os.getenv('KAFKA_API_SECRET')
}
producer = Producer(conf)

async def binance_stream():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@trade/ethusdt@trade/solusdt@trade"
    
    async with websockets.connect(uri) as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            
            trade_event = {
                "symbol": data['s'],      # BTCUSDT
                "price": float(data['p']),
                "volume": float(data['q']),
                "time": data['T']
            }
            
            with tracer.trace("kafka.produce") as span:
                producer.produce(
                    'crypto-trades',
                    key=trade_event['symbol'],
                    value=json.dumps(trade_event)
                )
                span.set_tag("symbol", trade_event['symbol'])
            
            if int(data['T']) % 10 == 0:
                producer.poll(0)
```

**Milestone:** See trades in Confluent Cloud dashboard

---

### Phase 2: The Brain (Day 2)
**Goal:** Consumer → Gemini analysis

```python
# backend/app/services/analyzer.py
from confluent_kafka import Consumer
import google.generativeai as genai
from ddtrace import tracer

model = genai.GenerativeModel('gemini-1.5-flash')

async def process_market_stream():
    consumer = Consumer({
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'group.id': 'ai-processor-group',
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe(['crypto-trades'])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        
        trade = json.loads(msg.value())
        rsi = calculate_rsi(trade['symbol'], trade['price'])
        
        if rsi > 80:
            await trigger_ai_analysis(trade, rsi)

async def trigger_ai_analysis(trade, rsi):
    prompt = f"""
    You are a crypto commentator.
    {trade['symbol']} just hit RSI of {rsi} at price {trade['price']}.
    Is this a pump or a trap?
    Answer in 1 sentence. Make it exciting.
    """
    
    with tracer.trace("gemini.generate"):
        response = await model.generate_content_async(prompt)
        text = response.text
    
    await voice_service.broadcast_audio(text)
```

**Milestone:** See Gemini responses in console

---

### Phase 3: The Mouth (Day 3)
**Goal:** ElevenLabs streaming audio

```python
# backend/app/services/voice.py
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from ddtrace import tracer

client = ElevenLabs(api_key=os.getenv('ELEVEN_API_KEY'))

async def broadcast_audio(text: str):
    with tracer.trace("elevenlabs.generate"):
        audio_stream = client.generate(
            text=text,
            voice="Brian",
            model="eleven_turbo_v2_5",
            stream=True
        )
    
    for chunk in audio_stream:
        await websocket_manager.broadcast(chunk)
```

**Milestone:** Hear AI speak in browser

---

### Phase 4: The Face (Day 4)
**Goal:** React dashboard with TradingView

```typescript
// frontend/src/hooks/useCryptoStream.ts
const useCryptoStream = () => {
    const chartRef = useRef<IChartApi | null>(null);
    
    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/ws");
        
        ws.onmessage = (event) => {
            if (event.data instanceof Blob) {
                // Audio → Play immediately
                playAudioBuffer(event.data);
            } else {
                // JSON → Update chart (no React state!)
                const trade = JSON.parse(event.data);
                chartRef.current?.update({
                    time: trade.time,
                    value: trade.price
                });
            }
        };
        
        return () => ws.close();
    }, []);
    
    return { chartRef };
};
```

**Milestone:** Full dashboard working

---

### Phase 5: The Proof (Day 5)
**Goal:** Datadog traces + demo video

```bash
# Run with Datadog tracing
ddtrace-run uvicorn app.main:app --reload
```

**Milestone:** Traces visible in Datadog APM

---

## 🎨 Frontend Layout Code

The exact "Bento Grid" layout matching the UI design.

**File: `frontend/src/app/dashboard/page.tsx`**

```tsx
import { LiveChart } from "@/components/LiveChart";
import { AIPulse } from "@/components/AIPulse";
import { MarketOverview } from "@/components/MarketOverview";
import { KafkaLogs } from "@/components/KafkaLogs";

export default function DashboardPage() {
  const handleForceAlert = async () => {
    await fetch("http://localhost:8000/debug/trigger", { method: "POST" });
  };

  return (
    <div className="min-h-screen bg-slate-950 p-4 text-slate-100">
      {/* Header */}
      <header className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
          ✦ PulseTrade AI: Crypto Edition
        </h1>
        <div className="flex gap-2">
          {/* Force Trigger Button for Demo */}
          <button 
            onClick={handleForceAlert}
            className="rounded bg-red-600 px-4 py-2 text-sm font-bold hover:bg-red-700 transition-colors"
          >
            🚨 FORCE ALERT
          </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="grid h-[calc(100vh-100px)] grid-cols-12 grid-rows-6 gap-4">
        
        {/* 1. Real Time Chart (Top Left - Large) */}
        <div className="col-span-8 row-span-4 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-slate-400">Real Time Chart</h2>
            <span className="text-xs text-emerald-400">● LIVE</span>
          </div>
          <LiveChart />
        </div>

        {/* 2. AI Pulse (Top Right - Medium) */}
        <div className="col-span-4 row-span-2 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent pointer-events-none" />
          <h2 className="text-sm font-semibold text-slate-400 mb-2">AI Pulse (Gemini + ElevenLabs)</h2>
          <AIPulse />
        </div>

        {/* 3. Market Overview (Middle Right - Medium) */}
        <div className="col-span-4 row-span-2 rounded-xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
          <h2 className="text-sm font-semibold text-slate-400 mb-2">Market Overview</h2>
          <MarketOverview />
        </div>

        {/* 4. Live Trade Stream / Kafka Logs (Bottom - Wide) */}
        <div className="col-span-12 row-span-2 rounded-xl border border-slate-800 bg-slate-950 shadow-inner overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
            <h2 className="text-sm font-semibold text-slate-400">Live Trade Stream (Kafka)</h2>
            <span className="text-xs text-cyan-400 font-mono">crypto-trades</span>
          </div>
          <KafkaLogs />
        </div>

      </div>
    </div>
  );
}
```

### Component Stubs

**File: `frontend/src/components/AIPulse.tsx`**

```tsx
"use client";
import { useEffect, useState } from "react";

export function AIPulse() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("Waiting for market signals...");

  return (
    <div className="flex flex-col h-full">
      {/* Glowing Pulse Circle */}
      <div className="flex-1 flex items-center justify-center">
        <div 
          className={`w-24 h-24 rounded-full transition-all duration-500 ${
            isSpeaking 
              ? "bg-emerald-500 shadow-[0_0_60px_20px_rgba(16,185,129,0.5)] animate-pulse" 
              : "bg-emerald-500/30 shadow-[0_0_20px_5px_rgba(16,185,129,0.2)]"
          }`}
        />
      </div>
      
      {/* Transcript Box */}
      <div className="mt-4 p-3 rounded-lg bg-slate-800/50 border border-slate-700">
        <p className="text-xs text-slate-400 mb-1">Latest voice transcript:</p>
        <p className="text-sm text-white">{transcript}</p>
      </div>
    </div>
  );
}
```

**File: `frontend/src/components/MarketOverview.tsx`**

```tsx
"use client";

interface Asset {
  symbol: string;
  name: string;
  price: number;
  change: number;
}

export function MarketOverview() {
  const assets: Asset[] = [
    { symbol: "ETH/USDT", name: "Ethereum", price: 67540.50, change: 1.85 },
    { symbol: "SOL/USDT", name: "Solana", price: 0.00035, change: -0.83 },
  ];

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-3 text-xs text-slate-500 px-2">
        <span>Name</span>
        <span className="text-right">Price</span>
        <span className="text-right">% Δ</span>
      </div>
      
      {assets.map((asset) => (
        <div 
          key={asset.symbol}
          className="grid grid-cols-3 items-center p-2 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500" />
            <div>
              <p className="text-sm font-medium text-white">{asset.symbol}</p>
              <p className="text-xs text-slate-500">{asset.name}</p>
            </div>
          </div>
          <span className="text-sm text-right font-mono text-white">
            {asset.price.toLocaleString()}
          </span>
          <span className={`text-sm text-right font-mono ${
            asset.change >= 0 ? "text-emerald-400" : "text-red-400"
          }`}>
            {asset.change >= 0 ? "+" : ""}{asset.change}%
          </span>
        </div>
      ))}
    </div>
  );
}
```

**File: `frontend/src/components/KafkaLogs.tsx`**

```tsx
"use client";
import { useEffect, useRef, useState } from "react";

interface LogEntry {
  s: string;  // Symbol
  p: number;  // Price
  q: number;  // Quantity
  T: number;  // Timestamp
}

export function KafkaLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div 
      ref={containerRef}
      className="h-full overflow-y-auto font-mono text-xs p-4 space-y-1"
    >
      {logs.map((log, i) => (
        <div key={i} className="text-slate-400">
          <span className="text-slate-600">{"{"}</span>
          <span className="text-cyan-400">"s"</span>: 
          <span className="text-emerald-400">"{log.s}"</span>, 
          <span className="text-cyan-400">"p"</span>: 
          <span className="text-amber-400">{log.p}</span>, 
          <span className="text-cyan-400">"q"</span>: 
          <span className="text-amber-400">{log.q}</span>, 
          <span className="text-cyan-400">"T"</span>: 
          <span className="text-purple-400">{log.T}</span>
          <span className="text-slate-600">{"}"}</span>
        </div>
      ))}
      {logs.length === 0 && (
        <div className="text-slate-500 animate-pulse">
          Connecting to Kafka stream...
        </div>
      )}
    </div>
  );
}
```

---

## 🎤 Voice AI Trigger Logic

### When AI Speaks

| Trigger | Condition | Cooldown | Example Output |
|---------|-----------|----------|----------------|
| **Whale Alert** | Price moves >1% in 1 min | 2 min | "Sudden volatility in Bitcoin! Price spiked 1.2%..." |
| **Sniper Signal** | RSI > 80 or RSI < 20 | 5 min | "Ethereum is extremely overbought with RSI of 82..." |
| **Psychological Level** | Price crosses $68k, $69k, $70k | 5 min | "Bitcoin smashed through 68,000 resistance!" |

### Cooldown Mechanism (Spam Prevention)

```python
# In-memory cooldown tracker
last_alert_time = {}  # Format: {"BTCUSDT_RSI": timestamp}

async def check_triggers(symbol, price, rsi, volume_spike):
    current_time = time.time()
    
    # Trigger 1: RSI EXTREME
    if rsi > 80:
        if not is_in_cooldown(symbol, "RSI_HIGH", current_time):
            await trigger_voice_alert(symbol, f"RSI peaking at {rsi}!")
            set_cooldown(symbol, "RSI_HIGH", current_time, 300)  # 5 min
    
    # Trigger 2: VOLATILITY PUMP
    elif volume_spike > 5.0:  # 5x normal volume
        if not is_in_cooldown(symbol, "VOLATILITY", current_time):
            await trigger_voice_alert(symbol, f"Massive volume spike!")
            set_cooldown(symbol, "VOLATILITY", current_time, 120)  # 2 min

def is_in_cooldown(symbol, alert_type, now):
    key = f"{symbol}_{alert_type}"
    last_time = last_alert_time.get(key, 0)
    return (now - last_time) < 300  # Default 5 min
```

### Demo Cheat Code
For the demo video, create a "Force Trigger" button:

```python
@app.post("/debug/trigger")
async def force_trigger():
    # Inject fake $100k BTC event
    fake_trade = {"symbol": "BTCUSDT", "price": 100000, "volume": 999}
    await trigger_ai_analysis(fake_trade, rsi=95)
    return {"status": "triggered"}
```

---

## 🖥 UI Component Breakdown

![Dashboard Reference](./uploaded_image_1766829393495.png)

### 1. Real Time Chart (Top Left)
- **Component:** `LiveChart.tsx`
- **Library:** TradingView Lightweight Charts
- **Features:** Candlesticks, volume bars, timeframe selector
- **Data:** WebSocket JSON updates (no React state)

### 2. AI Pulse Panel (Top Right)
- **Component:** `AIPulse.tsx`
- **Elements:**
  - Glowing green circle (pulses when speaking)
  - Transcript box showing Gemini's text
  - Header: "AI Pulse (Gemini + ElevenLabs)"

### 3. Market Overview (Middle Right)
- **Component:** `MarketOverview.tsx`
- **Elements:**
  - ETH/USDT, SOL/USDT prices
  - Green/red percentage changes
- **Purpose:** Show multi-symbol tracking

### 4. Live Trade Stream (Bottom)
- **Component:** `KafkaLogs.tsx`
- **Elements:**
  - Scrolling JSON: `{"s": "BTCUSDT", "p": 67540.50...}`
  - Fast-scrolling raw data
- **Purpose:** Prove Kafka streaming to judges

---

## 🔐 Environment Variables

```env
# === CORE ===
ENV=development
PORT=8000

# === GOOGLE (AI) ===
GOOGLE_API_KEY=AIzaSy...

# === ELEVENLABS (Voice) ===
ELEVEN_API_KEY=sk_...
ELEVEN_VOICE_ID=Brian

# === CONFLUENT (Streaming) ===
# Get from: https://confluent.cloud (free tier)
KAFKA_BOOTSTRAP_SERVERS=pkc-xyz.us-central1.gcp.confluent.cloud:9092
KAFKA_API_KEY=...
KAFKA_API_SECRET=...

# === DATADOG (Observability) ===
# Get from: https://datadoghq.com (free trial)
DD_API_KEY=...
DD_SITE=datadoghq.com
DD_SERVICE=pulsetrade-crypto
DD_ENV=development
```

---

## 📅 Execution Strategy

| Day | Focus | Milestone |
|-----|-------|-----------|
| **Day 1** | The Firehose | Trades flowing into Confluent Cloud |
| **Day 2** | The Brain | Gemini responses in console |
| **Day 3** | The Mouth | Hear AI speak in browser |
| **Day 4** | The Face | Full React dashboard working |
| **Day 5** | The Proof | Datadog traces + demo video |

---

## 🎬 Demo Video Outline (3 min)

| Time | Content |
|------|---------|
| 0:00-0:30 | **Problem:** Info overload in crypto trading |
| 0:30-1:30 | **Demo:** Real-time voice alerts (trigger with Force button) |
| 1:30-2:30 | **Datadog:** Show LLM observability dashboard |
| 2:30-3:00 | **Architecture:** Binance → Kafka → Gemini → ElevenLabs |

---

## ✅ Git Workflow

```bash
# Create new branch for crypto edition
git checkout -b feature/crypto-edition

# After each phase, commit
git add .
git commit -m "Phase 1: Binance → Kafka pipeline working"

# Push and create PR
git push origin feature/crypto-edition
```

---

## 📚 Required Packages

### Backend (`requirements.txt`)
```
fastapi==0.109.0
uvicorn==0.27.0
websockets==12.0
confluent-kafka==2.3.0
google-generativeai==0.3.2
elevenlabs==1.0.0
ddtrace==2.4.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
orjson==3.9.10
```

### Frontend (`package.json` additions)
```json
{
  "dependencies": {
    "lightweight-charts": "^4.1.0"
  }
}
```

---

## 🚨 Critical Rules

1. **No Polling** - Everything is WebSocket/stream-based
2. **No React State for Charts** - Use refs to avoid re-renders
3. **Cooldowns on Voice** - Never spam the same alert
4. **Trace Everything** - Datadog spans on Kafka, Gemini, ElevenLabs
5. **Keep prompts short** - Gemini responses under 30 words for TTS
