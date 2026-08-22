# AdaptRoute-Edu 🎓

> **An Adaptive AI Tutoring System featuring Multi-LLM Contextual Bandit Routing, Bayesian Knowledge Tracing (BKT), Multi-Agent Socratic Tutoring, and Vector Grounded RAG.**
> *B.Tech Final Year Project*

---

## 🌟 Overview

**AdaptRoute-Edu** is an end-to-end adaptive learning platform designed to personalize educational content, optimize model routing, and continuously estimate student mastery.

### Core Features

1. **Learning-Based Multi-LLM Adaptive Router**:
   - Dynamic model routing (Llama 3.1 8B, Gemma 2 9B, Mistral 7B, Phi 3.5).
   - Dual policy engine: **Heuristic Policy** (rules-based task-to-model matching) & **Contextual Bandit Policy (LinUCB)** (multi-objective reward function optimizing Pass Rate, Latency Efficiency, and Cost).
   - Real-time **Telemetry Dashboard** (`/telemetry`).

2. **Student Knowledge Tracing (BKT Engine)**:
   - Corbett & Anderson (1994) **Bayesian Knowledge Tracing** math engine calculating posterior concept mastery $P(L_t)$.
   - Real-time updates triggered automatically on quiz attempt submissions.
   - Interactive **Knowledge Mastery Heatmap** (`/progress`).

3. **Multi-Agent Collaborative Tutoring System**:
   - **Curriculum Planning Agent**: Formulates pedagogical next-step directives based on BKT mastery scores.
   - **Diagnostic Critic Agent**: Analyzes wrong quiz answers to pinpoint cognitive misconception patterns.
   - **Socratic Tutor Agent**: Executes guided step-by-step Socratic Q&A dialogue.
   - Interactive **Socratic Chat UI** embedded on study pages (`/topic/[id]`).

4. **Retrieval-Augmented Generation (RAG)**:
   - Vector similarity search over indexed course material with Cosine Similarity.
   - Injects verifiable reference source citations into LLM study notes and Socratic answers (`/rag/index`, `/rag/search`).

5. **Pure Black & White Typography Design System**:
   - Ultra-clean, high-contrast B&W aesthetic with electric indigo (`#6366F1`) accent CTAs and active navigation states.

6. **Production Architecture & Protection**:
   - In-memory sliding window **Rate Limiter** protecting LLM endpoints (`rate_limiter.py`).
   - High-contrast **Skeleton UI Loaders**.
   - Unified **Production Docker Compose** configuration (`db`, `ollama`, `backend`, `frontend`).

---

## 🏗️ System Architecture

```
User Request / Web Client (Next.js 14 Standalone)
                         │
                         ▼
        FastAPI Backend (Production Uvicorn)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
Multi-LLM Router    BKT Engine      RAG Vector Store
(LinUCB Bandit)  (Corbett&Anderson) (Cosine Similarity)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
         Multi-Agent Tutor Orchestrator
         ├── Curriculum Planning Agent
         ├── Diagnostic Critic Agent
         └── Socratic Tutor Agent
                         │
                         ▼
          PostgreSQL (Port 5433/5432)
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 20+
- Docker & Docker Desktop (optional for production containerization)

### 2. Local Environment Setup

#### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** in your browser.

---

## 🧪 Verification & Testing

Run full backend unit test suite:
```bash
cd backend
python -m pytest app/tests -v
# 43 / 43 PASSED
```

Run frontend type check:
```bash
cd frontend
npx tsc --noEmit
# 0 errors
```

Run live end-to-end system verification:
```bash
cd backend
python scripts/verify_system.py
# 9 / 9 Live Integration Steps PASSED
```

Seed demo data for presentation:
```bash
cd backend
python scripts/seed_demo_data.py
```

---

## 🐳 Production Docker Deployment

Deploy the full stack with a single command:
```bash
docker compose up --build -d
```

---

## 📜 License
Developed as a B.Tech Final Year Capstone Project. Open source under MIT License.
