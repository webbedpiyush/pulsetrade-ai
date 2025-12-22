# PulseTrade AI

Real-time multimodal trading assistant with AI-powered market analysis and voice alerts.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Gemini API key ([Get here](https://aistudio.google.com/apikey))
- ElevenLabs API key ([Get here](https://elevenlabs.io/app/settings/api-keys))

### 1. Clone & Setup

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

# Create .env file
cp .env.example .env
# Add your API keys to .env
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Run Both Services

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### 5. Open Dashboard
Visit http://localhost:3000

---

## 🐳 Docker Deployment

```bash
# Copy env file
cp backend/.env.example .env
# Edit .env with your API keys

# Run with Docker Compose
docker compose up --build
```

---

## 📊 Features

| Feature | Status |
|---------|--------|
| Yahoo Finance (NIFTY 50) | ✅ |
| Technical Indicators (SMA, VWAP) | ✅ |
| Breakout Detection | ✅ |
| Gemini 2.5 Flash Analysis | ✅ |
| ElevenLabs Voice Alerts | ✅ |
| Real-time Dashboard | ✅ |
| TradingView Charts | ✅ |

---

## 🏗 Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Yahoo Finance  │────▶│    FastAPI      │
│  (NIFTY 50)     │     │   Processing    │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌─────────┐  ┌─────────┐  ┌─────────┐
              │ Gemini  │  │ Eleven  │  │ WebSocket│
              │   AI    │  │  Labs   │  │  Stream │
              └────┬────┘  └────┬────┘  └────┬────┘
                   │            │            │
                   └────────────┴────────────┘
                                │
                         ┌──────▼──────┐
                         │   Next.js   │
                         │  Dashboard  │
                         └─────────────┘
```

---

## 📁 Project Structure

```
stock-alert/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI orchestrator
│   │   ├── config.py         # Settings
│   │   ├── ingestors/        # Market data sources
│   │   ├── processors/       # Technical indicators
│   │   ├── intelligence/     # Gemini AI
│   │   └── voice/            # ElevenLabs
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   └── stores/           # Zustand state
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🔧 Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Optional (for Kite Connect live data)
KITE_API_KEY=
KITE_ACCESS_TOKEN=
```

---

## 📜 License

MIT
