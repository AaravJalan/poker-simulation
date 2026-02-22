"""
Live analysis for 1-7 cards: win probability, hand distribution, best possible hand.
Convention: first 2 = hole cards, rest = board.
"""

import random
from collections import Counter
from typing import List, Optional, Dict

from poker_sim.monte_carlo import run_monte_carlo
from poker_sim.hand_eval import evaluate_7, _evaluate_5, rank, suit
from poker_sim.equity import HAND_NAMES, describe_hand

# Hand type IDs
HIGH_CARD, ONE_PAIR, TWO_PAIR, THREE_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_KIND, STRAIGHT_FLUSH = range(9)


def hand_distribution_and_win(
    hole_cards: List[int],
    board: List[int],
    num_opponents: int = 1,
    num_trials: int = 5000,
    seed: Optional[int] = None,
) -> Dict:
    """
    With hole_cards + board (any valid combo), run Monte Carlo and also sample
    hand type distribution (what hands hero makes over random board completions).
    """
    if len(hole_cards) != 2:
        return {"error": "Need exactly 2 hole cards"}
    if len(board) not in (0, 1, 2, 3, 4, 5):
        return {"error": "Board must have 0-5 cards"}

    used = set(hole_cards) | set(board)
    if len(used) != len(hole_cards) + len(board):
        return {"error": "Overlapping cards"}

    rng = random.Random(seed)
    hand_counts: Counter = Counter()
    wins = ties = losses = 0

    for _ in range(num_trials):
        deck = [c for c in range(52) if c not in used]
        rng.shuffle(deck)

        board_final = list(board)
        idx = 0
        while len(board_final) < 5:
            board_final.append(deck[idx])
            idx += 1

        opp_hands = []
        for _ in range(num_opponents):
            opp_hands.append([deck[idx], deck[idx + 1]])
            idx += 2

        hero_7 = list(hole_cards) + board_final
        hand_type, _ = evaluate_7(hero_7)
        hand_counts[hand_type] += 1

        hero_value = 1
        for opp in opp_hands:
            opp_hand = opp + board_final
            from poker_sim.hand_eval import compare_hands
            cmp = compare_hands(hero_7, opp_hand)
            if cmp < 0:
                hero_value = -1
                break
            if cmp == 0:
                hero_value = 0
        if hero_value > 0:
            wins += 1
        elif hero_value < 0:
            losses += 1
        else:
            ties += 1

    dist = {HAND_NAMES.get(ht, f"Type{ht}"): count / num_trials for ht, count in hand_counts.most_common()}
    best_hand_type = max(hand_counts.keys()) if hand_counts else -1

    return {
        "win_pct": wins / num_trials,
        "tie_pct": ties / num_trials,
        "loss_pct": losses / num_trials,
        "hand_distribution": dist,
        "best_possible_hand": HAND_NAMES.get(best_hand_type, "Unknown"),
        "equity": wins / num_trials + (ties / num_trials) / 2,
    }


def live_analysis(
    cards: List[int],
    num_opponents: int = 1,
    num_trials: int = 3000,
    seed: Optional[int] = None,
) -> Dict:
    """
    Analyze any number of cards (1-7).
    Convention: first 2 = hole, rest = board.
    - 1 card: not enough for sim; return card info only
    - 2 cards: assume hole cards, run preflop sim + hand distribution over random boards
    - 3-7 cards: first 2 = hole, rest = board; run full analysis
    """
    if len(cards) == 0:
        return {"error": "No cards selected", "win_pct": 0, "tie_pct": 0, "loss_pct": 0}

    if len(cards) == 1:
        r = rank(cards[0])
        s = suit(cards[0])
        return {
            "cards_count": 1,
            "message": "Select 2 hole cards for probability analysis.",
            "current_card": {"rank": r, "suit": s},
            "win_pct": 0,
            "tie_pct": 0,
            "loss_pct": 0,
            "hand_distribution": {},
            "best_possible_hand": "Need 2+ cards",
            "current_hand": None,
        }

    hole = cards[:2]
    board = cards[2:] if len(cards) > 2 else []

    if len(board) not in (0, 1, 2, 3, 4, 5):
        return {"error": "Invalid card count", "win_pct": 0, "tie_pct": 0, "loss_pct": 0}

    result = hand_distribution_and_win(hole, board, num_opponents, num_trials, seed)

    if "error" in result:
        return result

    current_hand = None
    if len(cards) >= 5:
        desc = describe_hand(cards)
        current_hand = desc["hand_name"]
        # With 5+ cards, best possible = current hand (you're using all cards)
        result["best_possible_hand"] = current_hand

    result["cards_count"] = len(cards)
    result["hole_cards"] = hole
    result["board_cards"] = board
    result["current_hand"] = current_hand

    return result
