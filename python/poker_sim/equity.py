"""
Dynamic equity calculation: win % at each street (pre-flop, flop, turn, river).
Shows how probability evolves as each card is revealed.
"""

from typing import List, Optional

from poker_sim.monte_carlo import run_monte_carlo
from poker_sim.hand_eval import (
    evaluate_7,
    card_str,
    HIGH_CARD,
    ONE_PAIR,
    TWO_PAIR,
    THREE_KIND,
    STRAIGHT,
    FLUSH,
    FULL_HOUSE,
    FOUR_KIND,
    STRAIGHT_FLUSH,
)

HAND_NAMES = {
    HIGH_CARD: "High Card",
    ONE_PAIR: "One Pair",
    TWO_PAIR: "Two Pair",
    THREE_KIND: "Three of a Kind",
    STRAIGHT: "Straight",
    FLUSH: "Flush",
    FULL_HOUSE: "Full House",
    FOUR_KIND: "Four of a Kind",
    STRAIGHT_FLUSH: "Straight Flush",
}


def equity_at_each_street(
    hole_cards: List[int],
    board: List[int],
    num_opponents: int = 1,
    num_trials: int = 5000,
    seed: Optional[int] = None,
) -> dict:
    """
    Run Monte Carlo at each street: pre-flop, flop, turn, river.
    For pre-flop, board=[]; flop=3 cards; turn=4; river=5.
    Returns equity (win%+tie%/2) at each street.
    """
    streets = []
    trials_per = max(500, num_trials // 4)  # Divide trials across streets

    # Pre-flop (board empty)
    if len(board) >= 0:
        r = run_monte_carlo(hole_cards, [], num_opponents, trials_per, seed)
        eq = r.win_rate() + r.tie_rate() / 2
        streets.append({"street": "preflop", "board_len": 0, "equity": eq, "win_pct": r.win_rate(), "tie_pct": r.tie_rate(), "loss_pct": r.loss_rate()})

    # Flop (3 cards)
    if len(board) >= 3:
        r = run_monte_carlo(hole_cards, board[:3], num_opponents, trials_per, seed)
        eq = r.win_rate() + r.tie_rate() / 2
        streets.append({"street": "flop", "board_len": 3, "equity": eq, "win_pct": r.win_rate(), "tie_pct": r.tie_rate(), "loss_pct": r.loss_rate()})

    # Turn (4 cards)
    if len(board) >= 4:
        r = run_monte_carlo(hole_cards, board[:4], num_opponents, trials_per, seed)
        eq = r.win_rate() + r.tie_rate() / 2
        streets.append({"street": "turn", "board_len": 4, "equity": eq, "win_pct": r.win_rate(), "tie_pct": r.tie_rate(), "loss_pct": r.loss_rate()})

    # River (5 cards)
    if len(board) >= 5:
        r = run_monte_carlo(hole_cards, board, num_opponents, trials_per, seed)
        eq = r.win_rate() + r.tie_rate() / 2
        streets.append({"street": "river", "board_len": 5, "equity": eq, "win_pct": r.win_rate(), "tie_pct": r.tie_rate(), "loss_pct": r.loss_rate()})

    return {"streets": streets}


def describe_hand(cards: List[int]) -> dict:
    """Describe hero's best 5-card hand from 5, 6, or 7 cards."""
    from itertools import combinations
    from poker_sim.hand_eval import _evaluate_5
    if len(cards) < 5:
        return {"hand_type_id": -1, "hand_name": "Need more cards", "tiebreaker": []}
    if len(cards) == 5:
        hand_type, tiebreaker = _evaluate_5(list(cards))
    elif len(cards) == 7:
        hand_type, tiebreaker = evaluate_7(cards)
    else:
        best = None
        for five in combinations(cards, 5):
            t, tb = _evaluate_5(list(five))
            if best is None or (t, tb) > best:
                best = (t, tb)
        hand_type, tiebreaker = best if best else (-1, ())
    return {
        "hand_type_id": hand_type,
        "hand_name": HAND_NAMES.get(hand_type, "Unknown"),
        "tiebreaker": list(tiebreaker) if tiebreaker else [],
    }


def get_potential_draws(hole_cards: List[int], board: List[int]) -> List[str]:
    """Identify draws hero could be on (flush draw, straight draw, etc.)."""
    from poker_sim.hand_eval import rank, suit
    from collections import Counter
    draws = []
    all_cards = list(hole_cards) + list(board)
    if len(all_cards) < 5:
        return draws
    suits_ct = Counter(suit(c) for c in all_cards)
    for s, cnt in suits_ct.items():
        if cnt == 4:
            draws.append("Flush draw (9 outs)")
            break
    ranks_set = set(rank(c) for c in all_cards)
    for high in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3]:
        needed = {(high - k) % 13 for k in range(5)}
        have = len(needed & ranks_set)
        if have == 4:
            draws.append("Straight draw (8 outs)")
            break
    if {12, 0, 1, 2, 3} & ranks_set and len({12, 0, 1, 2, 3} & ranks_set) >= 4:
        draws.append("Wheel draw (8 outs)")
    return draws


def hands_that_beat(hero_hand_type: int) -> List[str]:
    """Hand types that beat the given hand type."""
    stronger = []
    for ht, name in HAND_NAMES.items():
        if ht > hero_hand_type:
            stronger.append(name)
    return stronger

