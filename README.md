# NEPSE Intelligence — Nepal's First Open-Source Trading Dashboard

**The main dashboard every Nepali trader will use.**

Built for NEPSE realities: banking + hydro dominance, remittance sensitivity, geopolitical moves, and your secret correlations.

**Status**: Phase 1 complete (full-stack working!)

## Architecture

**Frontend** (React 18 + TypeScript + Vite)
- Live market dashboard with gainers/losers
- Real-time data via React Query (5s refresh)
- Responsive dark theme UI

**Backend** (FastAPI + Python)
- Live NEPSE API proxy endpoints
- PostgreSQL-backed endpoints for historical data
- 12+ REST API routes for stocks, indices, signals
- APScheduler for 5-minute data refresh

**Database** (PostgreSQL 15)
- 6 tables: indices, stocks, market_data, index_history, trading_signals
- Historical time-series data for charting & analysis
- Optimized indexes for performance

## Quick Start

```bash
# Using Docker (recommended)
docker compose up --build

# Or manually
# Backend:  cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
# Frontend: cd frontend && npm install && npm run dev
# DB:       PostgreSQL on localhost:5432 (credentials: nepse_user/nepse_password)
```

**Services:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

## Phase 1 Features

✅ Live market data from NEPSE API  
✅ PostgreSQL persistence layer  
✅ Data pipeline (5-min auto-refresh)  
✅ React dashboard (gainers, losers, all stocks)  
✅ REST API with 12+ endpoints  
✅ Full Docker Compose setup  
✅ Type-safe (TypeScript + Pydantic)  

## Phase 2 Roadmap

📊 Advanced charting (Recharts integration)  
🤖 ML-based trading signals  
💼 Portfolio tracking & backtesting  
📱 Mobile app (React Native)  
🔔 Real-time alerts & notifications  

## Project Structure

```
nepse-intelligence/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── database.py     # DB connection & init
│   │   ├── models.py       # SQLAlchemy ORM
│   │   ├── routes.py       # API endpoints
│   │   ├── pipeline.py     # Data fetcher/writer
│   │   ├── scheduler.py    # Background tasks
│   │   └── schemas.py      # Pydantic models
│   ├── requirements.txt
│   ├── schema.sql          # PostgreSQL schema
│   └── Dockerfile
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/Dashboard.tsx
│   │   ├── hooks/useQueries.ts
│   │   ├── api.ts          # Axios client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
└── docker-compose.yml      # 3-service orchestration
```

## Development

**Backend**
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://nepse_user:nepse_password@localhost:5432/nepse_intelligence
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Database**
```bash
# If not using Docker:
createdb -U postgres nepse_intelligence
psql -U postgres -d nepse_intelligence -f backend/schema.sql
```

## API Endpoints

**Live Data (from external NEPSE API)**
- `GET /api/live-market` - Real-time market data
- `GET /api/nepse-index` - NEPSE Index + sub-indices

**Historical Data (from PostgreSQL)**
- `GET /api/stocks` - All stocks with pagination
- `GET /api/stocks/{symbol}` - Single stock details
- `GET /api/stocks/{symbol}/history` - Price history (24h, 72h, 30d, etc.)
- `GET /api/indices` - All indices
- `GET /api/indices/{symbol}/history` - Index history
- `GET /api/market/top-gainers` - Top 10 gainers
- `GET /api/market/top-losers` - Top 10 losers
- `GET /api/market/summary` - Market totals & last update time
- `GET /api/signals` - Trading signals (filtered by symbol or type)

**Utilities**
- `GET /health` - API health check
- `GET /` - API info & available endpoints

## Environment Variables

**Backend (.env or docker-compose)**
```
DATABASE_URL=postgresql://nepse_user:nepse_password@db:5432/nepse_intelligence
ENVIRONMENT=development
```

**Frontend (vite.config.ts or .env)**
```
VITE_API_URL=http://localhost:8000  # or http://backend:8000 in Docker
```

## License

MIT - Open source trading intelligence for Nepal 🇳🇵

