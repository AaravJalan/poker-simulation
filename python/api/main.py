"""
FastAPI backend for poker simulation.
Run: cd python && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import time
import logging
from pathlib import Path

# Ensure poker_sim package is importable when running from repo root or python/
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    from poker_sim import run_monte_carlo, get_strategy_message
    from poker_sim.equity import equity_at_each_street, describe_hand, hands_that_beat, get_potential_draws
    from poker_sim.live_analysis import live_analysis
except ImportError as e:
    raise RuntimeError(
        f"Cannot import poker_sim (is the server running from the python/ directory?). {e}"
    ) from e

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Poker Simulation API",
    description="Monte Carlo Texas Hold'em win/tie/loss and EV feedback",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?|https://[a-zA-Z0-9-]+\.github\.io",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    hole_cards: list[int] = Field(..., min_length=2, max_length=2, description="2 card indices 0–51")
    board: list[int] = Field(default_factory=list, max_length=5, description="0, 3, 4, or 5 card indices")
    num_opponents: int = Field(default=1, ge=1, le=8)
    num_trials: int = Field(default=10000, ge=100, le=500000)


class SimulateResponse(BaseModel):
    win_pct: float
    tie_pct: float
    loss_pct: float
    strategy_message: str
    elapsed_ms: float | None = None




@app.get("/api/health")
def health():
    """Quick sanity check that simulation runs."""
    try:
        result = run_monte_carlo(hole_cards=[0, 1], board=[], num_opponents=1, num_trials=10)
        return {"ok": True, "win_pct": result.win_rate()}
    except Exception as e:
        logger.exception("Health check failed")
        raise HTTPException(status_code=500, detail=str(e))


class EquityByStreetResponse(BaseModel):
    streets: list
    elapsed_ms: float | None = None


class AnalyzeRequest(BaseModel):
    hole_cards: list[int] = Field(..., min_length=2, max_length=2)
    board: list[int] = Field(default_factory=list, max_length=5)


class AnalyzeResponse(BaseModel):
    hand_name: str
    hands_that_beat: list[str]
    potential_draws: list[str]
    elapsed_ms: float | None = None


class AuthRegisterRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=1)


class AuthLoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    id: str
    email: str
    name: str


@app.post("/api/auth/register", response_model=AuthResponse)
def auth_register(req: AuthRegisterRequest):
    """Register a new PokerID account. Email must be unique."""
    try:
        from poker_sim.auth_db import register
        user = register(req.email, req.password, req.username)
        return AuthResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Register failed")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/auth/login", response_model=AuthResponse)
def auth_login(req: AuthLoginRequest):
    """Login with PokerID (email + password)."""
    try:
        from poker_sim.auth_db import login
        user = login(req.email, req.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return AuthResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failed")
        raise HTTPException(status_code=500, detail="Login failed")


class ProfileUpdateRequest(BaseModel):
    user_id: str
    current_password: str
    new_username: str | None = None
    new_password: str | None = None


@app.post("/api/auth/update-profile", response_model=AuthResponse)
def auth_update_profile(req: ProfileUpdateRequest):
    try:
        import bcrypt
        from poker_sim.auth_db import _conn, update_username, update_password
        with _conn() as c:
            row = c.execute("SELECT id, email, password_hash, username FROM users WHERE id = ?", (req.user_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        if not bcrypt.checkpw(req.current_password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        user_id, email = row["id"], row["email"]
        name = row["username"] or email.split("@")[0]
        if req.new_password:
            update_password(user_id, req.current_password, req.new_password)
        if req.new_username is not None and req.new_username.strip():
            u = update_username(user_id, req.new_username)
            name = u["name"]
        return AuthResponse(id=user_id, email=email, name=name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class WinningsEntryRequest(BaseModel):
    user_id: str
    session_date: str
    buy_in: float = 0
    cash_out: float = 0
    hours: float = 0
    notes: str = ""


@app.post("/api/winnings")
def winnings_add(req: WinningsEntryRequest):
    try:
        from poker_sim.winnings_db import add_entry
        return add_entry(req.user_id, req.session_date, req.buy_in, req.cash_out, req.notes, req.hours)
    except Exception as e:
        logger.exception("Winnings add failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/winnings")
def winnings_list(user_id: str, period: str = "all"):
    try:
        from poker_sim.winnings_db import get_entries
        return {"entries": get_entries(user_id, period)}
    except Exception as e:
        logger.exception("Winnings list failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/winnings/{entry_id}")
def winnings_delete(entry_id: str, user_id: str):
    try:
        from poker_sim.winnings_db import delete_entry
        if not delete_entry(user_id, entry_id):
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"ok": True}
    except HTTPException:
        raise


@app.get("/api/friends")
def friends_list(user_id: str):
    try:
        from poker_sim.friends_db import get_friends
        return {"friends": get_friends(user_id)}
    except Exception as e:
        logger.exception("Friends list failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/friends/search")
def friends_search(user_id: str, q: str = ""):
    try:
        from poker_sim.friends_db import search_users
        return {"users": search_users(user_id, q)}
    except Exception as e:
        logger.exception("Friends search failed")
        raise HTTPException(status_code=500, detail=str(e))


class FriendAddRequest(BaseModel):
    user_id: str
    friend_id: str


@app.post("/api/friends")
def friends_add(req: FriendAddRequest):
    """Send a friend request. Recipient must accept in inbox."""
    try:
        from poker_sim.friends_db import send_friend_request
        send_friend_request(req.user_id, req.friend_id)
        return {"ok": True, "status": "request_sent"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/friends/inbox")
def friends_inbox(user_id: str):
    """Pending friend requests (incoming)."""
    try:
        from poker_sim.friends_db import get_pending_requests
        return {"requests": get_pending_requests(user_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/friends/sent")
def friends_sent(user_id: str):
    """User IDs we've sent requests to."""
    try:
        from poker_sim.friends_db import get_sent_requests
        return {"sent_to": list(get_sent_requests(user_id))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FriendRequestAction(BaseModel):
    user_id: str  # acceptor/decliner
    from_id: str  # who sent the request


@app.post("/api/friends/accept")
def friends_accept(req: FriendRequestAction):
    try:
        from poker_sim.friends_db import accept_friend_request
        accept_friend_request(req.user_id, req.from_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/friends/decline")
def friends_decline(req: FriendRequestAction):
    try:
        from poker_sim.friends_db import decline_friend_request
        decline_friend_request(req.user_id, req.from_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/friends/{friend_id}")
def friends_remove(friend_id: str, user_id: str):
    try:
        from poker_sim.friends_db import remove_friend
        remove_friend(user_id, friend_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/friends/all-users")
def friends_all_users(user_id: str, limit: int = 50):
    try:
        from poker_sim.friends_db import list_all_users
        return {"users": list_all_users(user_id, limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Games ----
class GameCreateRequest(BaseModel):
    user_id: str
    user_name: str


class GameJoinRequest(BaseModel):
    user_id: str
    user_name: str
    initial_buy_in: float = 0


class GameAddBuyInRequest(BaseModel):
    user_id: str
    amount: float


class GameLeaveRequest(BaseModel):
    user_id: str
    cash_out: float


class GameInviteRequest(BaseModel):
    host_id: str
    friend_ids: list[str] = Field(default_factory=list)


class GameAddPlayersRequest(BaseModel):
    host_id: str
    user_ids: list[str] = Field(default_factory=list)
    user_names: dict[str, str] = Field(default_factory=dict)


class GameEndRequest(BaseModel):
    user_id: str


@app.post("/api/games")
def games_create(req: GameCreateRequest):
    try:
        from poker_sim.games_db import create_game
        return create_game(req.user_id, req.user_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/games/by-code/{code}")
def games_get_by_code(code: str):
    try:
        from poker_sim.games_db import get_game_by_code
        g = get_game_by_code(code)
        if not g:
            raise HTTPException(status_code=404, detail="Game not found")
        return g
    except HTTPException:
        raise


@app.get("/api/games/{game_id}")
def games_get(game_id: str):
    try:
        from poker_sim.games_db import get_game
        g = get_game(game_id)
        if not g:
            raise HTTPException(status_code=404, detail="Game not found")
        return g
    except HTTPException:
        raise


@app.get("/api/games/user/{user_id}")
def games_list_user(user_id: str):
    try:
        from poker_sim.games_db import list_user_games
        return {"games": list_user_games(user_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/games/{game_id}/join")
def games_join(game_id: str, req: GameJoinRequest):
    try:
        from poker_sim.games_db import join_game
        return join_game(game_id, req.user_id, req.user_name, req.initial_buy_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/games/{game_id}/add-buy-in")
def games_add_buy_in(game_id: str, req: GameAddBuyInRequest):
    try:
        from poker_sim.games_db import add_buy_in
        return add_buy_in(game_id, req.user_id, float(req.amount))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("add-buy-in failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/games/{game_id}/leave")
def games_leave(game_id: str, req: GameLeaveRequest):
    try:
        from poker_sim.games_db import leave_game
        return leave_game(game_id, req.user_id, req.cash_out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/games/{game_id}/invite")
def games_invite(game_id: str, req: GameInviteRequest):
    """Invite friends to game. They must accept to join."""
    try:
        from poker_sim.games_db import invite_friends_to_game
        return invite_friends_to_game(game_id, req.host_id, req.friend_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/games/invites")
def games_pending_invites(user_id: str):
    """Get games this user is invited to."""
    try:
        from poker_sim.games_db import get_pending_game_invites
        return {"invites": get_pending_game_invites(user_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GameAcceptInviteRequest(BaseModel):
    user_id: str
    user_name: str
    initial_buy_in: float = 0


@app.post("/api/games/{game_id}/accept-invite")
def games_accept_invite(game_id: str, req: GameAcceptInviteRequest):
    try:
        from poker_sim.games_db import accept_game_invite
        return accept_game_invite(game_id, req.user_id, req.user_name, req.initial_buy_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class GameAddByEmailRequest(BaseModel):
    host_id: str
    email: str


class GameAddManualRequest(BaseModel):
    host_id: str
    name: str


@app.post("/api/games/{game_id}/add-by-email")
def games_invite_by_email(game_id: str, req: GameAddByEmailRequest):
    """Invite user by email. They must accept to join."""
    try:
        from poker_sim.games_db import invite_by_email
        return invite_by_email(game_id, req.host_id, req.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/games/{game_id}/add-manual")
def games_add_manual(game_id: str, req: GameAddManualRequest):
    try:
        from poker_sim.games_db import add_player_manually
        return add_player_manually(game_id, req.host_id, req.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/games/{game_id}/end")
def games_end(game_id: str, req: GameEndRequest):
    try:
        from poker_sim.games_db import end_game
        return end_game(game_id, req.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class GameRenameRequest(BaseModel):
    user_id: str
    name: str


@app.patch("/api/games/{game_id}")
def games_rename(game_id: str, req: GameRenameRequest):
    try:
        from poker_sim.games_db import rename_game
        return rename_game(game_id, req.user_id, req.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/games/{game_id}")
def games_delete(game_id: str, user_id: str = Query(..., description="Host user ID")):
    try:
        from poker_sim.games_db import delete_game
        delete_game(game_id, user_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: dict = Field(default_factory=dict)


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Poker AI assistant. Set OPENAI_API_KEY for GPT, else uses canned tips."""
    try:
        from poker_sim.chat_bot import get_chat_reply
        reply = get_chat_reply(req.message, req.context)
        return {"reply": reply}
    except Exception as e:
        logger.exception("Chat failed")
        raise HTTPException(status_code=500, detail=str(e))


class LiveAnalysisRequest(BaseModel):
    cards: list[int] = Field(..., min_length=1, max_length=7)
    num_opponents: int = Field(default=1, ge=1, le=8)
    num_trials: int = Field(default=3000, ge=500, le=50000)


@app.post("/api/live-analysis")
def api_live_analysis(req: LiveAnalysisRequest):
    """Live analysis for 1-7 cards: win %, hand distribution, best possible hand."""
    t0 = time.perf_counter()
    try:
        data = live_analysis(
            cards=req.cards,
            num_opponents=req.num_opponents,
            num_trials=req.num_trials,
        )
        elapsed = time.perf_counter() - t0
        logger.info(f"Live analysis: {len(req.cards)} cards, {req.num_trials} trials -> {elapsed:.3f}s")
        data["elapsed_ms"] = elapsed * 1000
        return data
    except Exception as e:
        logger.exception("Live analysis failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/equity-by-street", response_model=EquityByStreetResponse)
def equity_by_street(req: SimulateRequest):
    """Return equity (win% + tie%/2) at each street: preflop, flop, turn, river."""
    t0 = time.perf_counter()
    try:
        data = equity_at_each_street(
            hole_cards=req.hole_cards,
            board=req.board or [],
            num_opponents=req.num_opponents,
            num_trials=min(req.num_trials, 20000),
        )
        elapsed = time.perf_counter() - t0
        logger.info(f"Equity by street: {elapsed:.3f}s")
        return EquityByStreetResponse(streets=data["streets"], elapsed_ms=elapsed * 1000)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Equity by street failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """Describe hero's hand, what beats it, and potential draws."""
    t0 = time.perf_counter()
    try:
        all_cards = list(req.hole_cards) + list(req.board)
        if len(all_cards) < 5:
            return AnalyzeResponse(hand_name="Need 5+ cards", hands_that_beat=[], potential_draws=[])
        desc = describe_hand(all_cards)
        beat_by = hands_that_beat(desc["hand_type_id"]) if desc["hand_type_id"] >= 0 else []
        draws = get_potential_draws(req.hole_cards, req.board)
        elapsed = time.perf_counter() - t0
        logger.info(f"Analyze: {elapsed:.3f}s")
        return AnalyzeResponse(
            hand_name=desc["hand_name"],
            hands_that_beat=beat_by,
            potential_draws=draws,
            elapsed_ms=elapsed * 1000,
        )
    except Exception as e:
        logger.exception("Analyze failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest):
    t0 = time.perf_counter()
    try:
        result = run_monte_carlo(
            hole_cards=req.hole_cards,
            board=req.board if req.board else None,
            num_opponents=req.num_opponents,
            num_trials=req.num_trials,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Simulation failed")
        raise HTTPException(status_code=500, detail=str(e))
    elapsed = time.perf_counter() - t0
    logger.info(f"Simulation: {req.num_trials} trials -> {elapsed:.3f}s")
    win_pct = result.win_rate()
    tie_pct = result.tie_rate()
    return SimulateResponse(
        win_pct=win_pct,
        tie_pct=tie_pct,
        loss_pct=result.loss_rate(),
        strategy_message=get_strategy_message(win_pct, tie_pct),
        elapsed_ms=elapsed * 1000,
    )


@app.post("/api/scan-cards")
async def scan_cards(file: UploadFile = File(...)):
    """
    Scan playing cards from an image. Returns detected card indices (0-51) and
    bounding boxes [{x,y,w,h}, ...] in image pixel coords for tracking overlay.
    """
    t0 = time.perf_counter()
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        cards, boxes, img_w, img_h = _detect_cards_with_boxes(content)
        elapsed = time.perf_counter() - t0
        logger.info(f"Scan cards: {elapsed:.3f}s -> {len(cards)} cards, {len(boxes)} boxes")
        return {
            "cards": cards,
            "count": len(cards),
            "boxes": [{"x": b[0], "y": b[1], "w": b[2], "h": b[3]} for b in boxes],
            "img_width": img_w,
            "img_height": img_h,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Scan cards failed")
        raise HTTPException(status_code=500, detail=str(e))


def _detect_cards_with_boxes(image_bytes: bytes) -> tuple[list[int], list[tuple[int, int, int, int]], int, int]:
    try:
        from poker_sim.card_detector import detect_cards_with_boxes
        return detect_cards_with_boxes(image_bytes)
    except Exception:
        return [], [], 0, 0


# Serve built React app from same origin (no CORS). Must be last.
_static_dir = _root.parent / "web" / "dist"
if _static_dir.exists():
    assets_dir = _static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/")
def serve_index():
    """Serve React app or API info if no build."""
    index = _static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Poker Simulation API", "docs": "/docs"}


@app.get("/{path:path}")
def serve_spa(path: str):
    """Serve SPA routes (dashboard, login, etc.)."""
    if path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")
    fp = _static_dir / path
    if fp.exists() and fp.is_file():
        return FileResponse(fp)
    index = _static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Not found")
