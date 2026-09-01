# 🔍 LogMoni - Log Monitoring & Alerting System

A real-time log collection, analysis, and alerting platform designed to demonstrate **Data Engineering** skills including message queues, time-series aggregation, and streaming data processing.

## 🏗️ Architecture

```
Log Simulator → FastAPI (Producer) → RabbitMQ → Consumer Worker → PostgreSQL
                                                       ↓
                                              Alert Engine → WebSocket → React Dashboard
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Message Queue | RabbitMQ 3.13 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Frontend | React 18 + Vite 5 |
| Charts | Recharts |
| Real-time | WebSocket |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Start Infrastructure
```bash
docker-compose up -d
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 4. Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Start Log Simulator
```bash
cd simulator
pip install -r requirements.txt
python generate_logs.py --rate 10 --burst --error-spike
```

## 📊 Key Features

- **Async Processing**: RabbitMQ decouples log ingestion from processing
- **Window Functions**: PostgreSQL aggregation with `date_trunc`, `RANK()`, `LAG()`, `FILTER`
- **BRIN Index**: Optimized for time-series append-only data
- **Real-time Alerts**: WebSocket broadcasting for immediate notification
- **Auto-refresh Dashboard**: Line chart updates every 10 seconds

## 📁 Project Structure

```
LogMoni/
├── backend/          # FastAPI backend (Producer + Consumer + API)
│   ├── app/
│   │   ├── api/      # HTTP + WebSocket endpoints
│   │   ├── core/     # RabbitMQ + WebSocket managers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic validation
│   │   └── services/ # Business logic (Consumer, Aggregation, Alerts)
│   ├── alembic/      # Database migrations
│   └── tests/        # Pytest test suite
├── frontend/         # React + Vite dashboard
│   └── src/
│       ├── components/  # UI components
│       ├── hooks/       # Custom React hooks
│       └── services/    # API client
├── simulator/        # Fake log generator
├── sql/              # Raw SQL schema & queries
└── docker-compose.yml
```

## 🔗 URLs

| Service | URL |
|---------|-----|
| FastAPI Docs | http://localhost:8000/docs |
| RabbitMQ Management | http://localhost:15672 (logmoni/logmoni_secret) |
| Frontend Dashboard | http://localhost:5173 |

## 📄 License

MIT
