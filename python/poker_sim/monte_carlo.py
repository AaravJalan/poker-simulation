"""
Monte Carlo simulation for Texas Hold'em.
Given hero hole cards, optional board, and number of opponents, estimates win/tie/loss %.
Uses C++ extension when built for ~10-50x speedup.
"""

import random
from typing import List, Optional

try:
    from poker_sim.poker_sim_cpp import run_monte_carlo as _cpp_run
except ImportError:
    _cpp_run = None

from poker_sim.hand_eval import compare_hands


def run_monte_carlo(
    hole_cards: List[int],
    board: Optional[List[int]] = None,
    num_opponents: int = 1,
    num_trials: int = 10000,
    seed: Optional[int] = None,
) -> "SimResult":
    """
    Run Monte Carlo simulation.

    Args:
        hole_cards: Exactly 2 card indices (0–51).
        board: 0, 3, 4, or 5 card indices (flop/turn/river).
        num_opponents: Number of opponents (1–8).
        num_trials: Number of trials.
        seed: Optional RNG seed for reproducibility.

    Returns:
        SimResult with wins, ties, losses, total, win_rate(), tie_rate(), loss_rate().
    """
    if board is None:
        board = []
    if len(hole_cards) != 2:
        raise ValueError("hole_cards must have exactly 2 cards")
    if len(board) not in (0, 3, 4, 5):
        raise ValueError("board must have 0, 3, 4, or 5 cards")
    if not (1 <= num_opponents <= 8):
        raise ValueError("num_opponents must be 1–8")
    used = set(hole_cards) | set(board)
    if len(used) != len(hole_cards) + len(board):
        raise ValueError("hole_cards and board must not overlap")
    deck_size = 52 - len(used)
    need_per_trial = 5 - len(board) + num_opponents * 2  # remaining board + each opponent's 2
    if     need_per_trial > deck_size:
        raise ValueError("not enough cards in deck for this configuration")

    if _cpp_run is not None:
        r = _cpp_run(hole_cards, board, num_opponents, num_trials, seed)
        from poker_sim.types import SimResult
        return SimResult(wins=r.wins, ties=r.ties, losses=r.losses, total=num_trials)

    rng = random.Random(seed)
    wins = ties = losses = 0

    for _ in range(num_trials):
        deck = [c for c in range(52) if c not in used]
        rng.shuffle(deck)
        # Complete board
        board_final = list(board)
        idx = 0
        while len(board_final) < 5:
            board_final.append(deck[idx])
            idx += 1
        # Opponent hands
        opp_hands = []
        for _ in range(num_opponents):
            opp_hands.append([deck[idx], deck[idx + 1]])
            idx += 2
        hero_hand = list(hole_cards) + board_final
        hero_value = None
        best_opp_value = None
        for opp in opp_hands:
            opp_hand = opp + board_final
            cmp = compare_hands(hero_hand, opp_hand)
            if cmp > 0:
                hero_value = 1
                break
            if cmp < 0:
                if best_opp_value is None or best_opp_value < -1:
                    best_opp_value = -1
            else:
                if best_opp_value is None:
                    best_opp_value = 0
        if hero_value is None:
            hero_value = best_opp_value if best_opp_value is not None else 0
        if hero_value > 0:
            wins += 1
        elif hero_value < 0:
            losses += 1
        else:
            ties += 1

    from poker_sim.types import SimResult
    return SimResult(wins=wins, ties=ties, losses=losses, total=num_trials)


def get_strategy_message(win_pct: float, tie_pct: float) -> str:
    """Simple EV-oriented message for the UI."""
    equity = win_pct + tie_pct / 2
    if equity >= 0.65:
        return "Strong equity — consider betting or raising for value."
    if equity >= 0.50:
        return "Positive equity — betting or calling is often correct."
    if equity >= 0.35:
        return "Moderate equity — play depends on pot odds and opponent tendencies."
    if equity >= 0.20:
        return "Low equity — consider folding unless pot odds justify a call."
    return "Weak equity — folding is usually correct unless you have strong implied odds."
