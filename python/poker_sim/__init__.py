"""
Texas Hold'em Monte Carlo simulation – Python API.

Full simulation: hand evaluator + Monte Carlo engine.
Optionally uses C++ extension if built (see repository README).
"""

from poker_sim.types import SimResult
from poker_sim.hand_eval import (
    RANKS,
    SUITS,
    card_str,
    rank,
    suit,
    evaluate_7,
    compare_hands,
)
from poker_sim.monte_carlo import run_monte_carlo, get_strategy_message, get_suggested_action


def run_simulation(
    num_trials: int = 10000,
    hole_cards: list = None,
    board: list = None,
    num_opponents: int = 1,
    seed: int = None,
):
    """
    Run Monte Carlo simulation.

    With hole_cards (and optional board): full Texas Hold'em simulation.
    With only num_trials (legacy): placeholder random outcome.

    Args:
        num_trials: Number of simulated hands.
        hole_cards: Optional list of 2 card indices (0–51).
        board: Optional list of 0, 3, 4, or 5 card indices.
        num_opponents: Number of opponents (1–8).
        seed: Optional RNG seed.

    Returns:
        SimResult with wins, ties, losses, total, win_rate(), tie_rate(), loss_rate().
    """
    if hole_cards is not None and len(hole_cards) == 2:
        return run_monte_carlo(
            hole_cards=hole_cards,
            board=board or [],
            num_opponents=num_opponents,
            num_trials=num_trials,
            seed=seed,
        )
    # Legacy: no hole cards – use Python placeholder
    import random
    rng = random.Random(seed or 12345)
    wins = ties = 0
    for _ in range(num_trials):
        outcome = rng.randint(0, 2)
        if outcome == 0:
            wins += 1
        elif outcome == 1:
            ties += 1
    return SimResult(wins=wins, ties=ties, total=num_trials, losses=num_trials - wins - ties)


__all__ = [
    "run_simulation",
    "run_monte_carlo",
    "SimResult",
    "get_strategy_message",
    "get_suggested_action",
    "card_str",
    "RANKS",
    "SUITS",
    "rank",
    "suit",
    "evaluate_7",
    "compare_hands",
]
