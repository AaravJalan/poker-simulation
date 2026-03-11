# Poker Simulation

A Texas Hold'em poker decision-support app with Monte Carlo simulations, hand analysis, session tracking, friends, and live games.

### Website

Live app: `https://poker-simulation.vercel.app/`

---

## Purpose

- Quickly estimate **win/tie/loss** and **equity** from any street (preflop → river)
- Explain *why* (hand analysis + draws) instead of just showing a percentage
- Track results over time (sessions + winnings)

---

## Features

### Simulator

- **Tap-to-pick cards** (hole + board) with a visual deck grid (mobile-friendly layout)
- **Live probability** while selecting cards (fast approximation)
- **Run simulation** for a more accurate Monte Carlo result
- **Equity by street** chart (how equity changes as community cards arrive)
- **Hand analysis** (current best hand, hands that beat you, potential draws)
- **AI assistant** (optional): poker Q&A if `OPENAI_API_KEY` is configured

### Past Simulations

- Save runs to `localStorage` and revisit previous simulations

### Winnings

- Track sessions: **date, buy-in, cash-out, hours, notes**
- Stats and a cumulative **profit over time** graph

### Friends

- Search and add friends
- Inbox for friend requests

### Games

- Create games with a **join code**
- Invite friends / add manual players (no account)
- Track **buy-ins**, **cash-outs**, and **settlements**

### Hand Hierarchy

- Reference page for poker hand rankings

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | **React + TypeScript** (Vite) |
| UI | CSS styling |
| Backend API | **FastAPI** (Python) |
| Simulation | Monte Carlo evaluator (Python) |
| Auth + DB (prod) | **Supabase Auth + Postgres** |
| Local dev DB/auth (default) | SQLite + PokerID (bcrypt) |
| Hosting | **Vercel** (static frontend + Python serverless functions) |
| AI (optional) | OpenAI API (falls back to canned tips if unset) |
| Card scanning (optional/local) | OpenCV-based template matching |

---

## Programming Languages

- **TypeScript**: frontend web app (React)
- **Python**: backend API (FastAPI) + simulation logic
- **C++**: native hand evaluation + simulation core (`cpp/`)
- **SQL**: Supabase Postgres schema/migrations (`supabase/schema.sql`)
- **Shell**: helper scripts (e.g. `run_api.sh`)

---

## How to Run Locally

### Requirements (software)

- **Node.js** 18+
- **Python** 3.9+

### 1) Start the backend (FastAPI)

From the repo root:

```bash
./run_api.sh
```

API runs at **`http://127.0.0.1:8000`**.

### 2) Start the frontend (Vite)

```bash
cd web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

App runs at **`http://127.0.0.1:5173`** and calls the backend via `/api`.

---

## Optional: Supabase locally

Local dev defaults to **SQLite + PokerID**. To use **Supabase** locally:

### Frontend env (`web/.env`)

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

### Backend env (before starting API)

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

For Google sign-in in local dev, allowlist redirect URLs in **Supabase → Authentication → URL Configuration**:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

---
