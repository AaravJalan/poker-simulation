# Poker Simulation

A Texas Hold'em poker decision-support app with Monte Carlo simulations, hand analysis, session tracking, friends, and live games.

## Features

### Simulator
- **Card selection**: Pick 2 hole cards and 0–5 board cards from a visual grid, or scan via camera
- **Live probability**: Win/tie/loss % updates as you select cards (2–7 cards)
- **Equity by street**: Line graph of win probability at preflop, flop, turn, river (2 → 5 → 6 → 7 cards)
- **Best possible hand**: Shown live when 5+ cards are selected
- **Action tile**: Suggests "Bet" or "Check / Fold" based on equity
- **Hand analysis**: Current hand, hands that beat you, potential draws
- **AI assistant**: Chat panel (top-right) for poker questions; uses OpenAI if `OPENAI_API_KEY` is set, else canned tips

### My simulations
- Save runs to localStorage and revisit past simulations

### Winnings
- Track sessions: date, buy-in, cash-out, hours, notes
- Stats: total profit, sessions, hours, profitable ratio, profit/hour
- Line graph of cumulative profit over time (on the right)

### Friends
- Add friends via search (email/username)
- Friend requests: send request → they accept in inbox
- Remove friends

### Games
- Create games with a join code
- Invite by PokerID (email) or select friends — they get a request and must accept
- Add players manually (no account)
- Track buy-ins, cash-outs, settlements
- Rename and delete games (host only)
- Add session to winnings when leaving a game

### Hand hierarchy
- Reference page for poker hand rankings

### Card scanning
- Live camera scan with tracking boxes around detected cards
- Run `python3 scripts/download_card_imgs.py` to fetch card templates (OpenCV-based detection)

---

## Tech Stack

| Layer        | Technology |
|-------------|------------|
| Simulation  | **Python** (Monte Carlo, hand evaluator) / **C++** (optional, pybind11) |
| API         | **Python** – FastAPI |
| Frontend    | **React** (TypeScript, Vite) – neumorphic UI |
| Database    | SQLite (users, friends, games, winnings) |
| Auth        | bcrypt (PokerID) / Supabase (optional) |
| Card detection | OpenCV, template matching |
| AI          | OpenAI API (optional) or canned responses |

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register (email, password) |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/update-profile` | Rename, change password |
| GET | `/api/winnings` | List winnings entries |
| POST | `/api/winnings` | Add entry |
| DELETE | `/api/winnings/{id}` | Delete entry |
| GET | `/api/friends` | List friends |
| GET | `/api/friends/search` | Search users |
| POST | `/api/friends` | Send friend request |
| GET | `/api/friends/inbox` | Pending requests |
| GET | `/api/friends/sent` | Sent requests |
| POST | `/api/friends/accept` | Accept request |
| POST | `/api/friends/decline` | Decline request |
| DELETE | `/api/friends/{id}` | Remove friend |
| GET | `/api/friends/all-users` | List all users |
| POST | `/api/games` | Create game |
| GET | `/api/games/user/{id}` | User's games |
| GET | `/api/games/{id}` | Game details |
| GET | `/api/games/by-code/{code}` | Find by join code |
| POST | `/api/games/{id}/join` | Join with code |
| POST | `/api/games/{id}/invite` | Invite friends |
| GET | `/api/games/invites` | Pending game invites |
| POST | `/api/games/{id}/accept-invite` | Accept invite |
| POST | `/api/games/{id}/add-by-email` | Invite by email |
| POST | `/api/games/{id}/add-manual` | Add manual player |
| POST | `/api/games/{id}/add-buy-in` | Add buy-in |
| POST | `/api/games/{id}/leave` | Leave with cash-out |
| POST | `/api/games/{id}/end` | End game (host) |
| PATCH | `/api/games/{id}` | Rename game |
| DELETE | `/api/games/{id}` | Delete game |
| POST | `/api/simulate` | Run Monte Carlo |
| POST | `/api/live-analysis` | Live win % (1–7 cards) |
| POST | `/api/equity-by-street` | Equity at each street |
| POST | `/api/analyze` | Hand analysis |
| POST | `/api/scan-cards` | Detect cards from image |
| POST | `/api/chat` | AI chatbot |

---

## How to Run

### 1. Python (API)

```bash
cd python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the API

From repo root:
```bash
./run_api.sh
```

Or manually:
```bash
cd python && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API: **http://localhost:8000**

### 3. Start the web app

```bash
cd web
npm install
npm run dev
```

App: **http://localhost:5173** (proxies `/api` to port 8000)

---

## How to Use

1. **Sign in** with email (and optional display name)
2. **Simulator**: Select 2 hole cards + 0–5 board cards. Click **Run simulation** or watch live odds
3. **Camera**: Click 📷 to scan cards (green boxes show detected regions)
4. **AI**: Click 🤖 (top-right) to ask poker questions
5. **Winnings**: Add sessions manually or from games when leaving
6. **Friends**: Search, send request; they accept in inbox
7. **Games**: Create game, share join code, invite by email or friends; they accept to join

---

## Card encoding

Cards use indices **0–51**:
- Rank = `card % 13` (0=2 … 12=A)
- Suit = `card // 13` (0=♣ 1=♦ 2=♥ 3=♠)

---

## Optional: C++ extension

For faster simulations:
```bash
mkdir build && cd build
cmake ..
cmake --build .
cmake --install . --prefix ..
```

Requires CMake ≥ 3.15 and a C++17 compiler.

---

## Optional: Card templates

For camera detection:
```bash
python3 scripts/download_card_imgs.py
```

---

## Prerequisites

- **Python** 3.9+
- **Node.js** 18+
- **C++** (optional): C++17, CMake ≥ 3.15
