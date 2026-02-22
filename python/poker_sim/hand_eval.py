"""
Texas Hold'em hand evaluator.
Cards: 0–51. rank = card % 13 (0=2 … 12=A), suit = card // 13 (0=♣ 1=♦ 2=♥ 3=♠).
"""

from itertools import combinations
from collections import Counter
from typing import List, Tuple

# Hand rank order (higher = stronger)
HIGH_CARD, ONE_PAIR, TWO_PAIR, THREE_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_KIND, STRAIGHT_FLUSH = range(9)

RANKS = "23456789TJQKA"
SUITS = "♣♦♥♠"


def card_str(card: int) -> str:
    return RANKS[card % 13] + SUITS[card // 13]


def rank(card: int) -> int:
    return card % 13


def suit(card: int) -> int:
    return card // 13


def _ranks_sorted(cards: List[int], reverse: bool = True) -> List[int]:
    r = sorted([rank(c) for c in cards], reverse=reverse)
    return r


def _evaluate_5(cards: List[int]) -> Tuple[int, Tuple[int, ...]]:
    """Return (hand_type, tiebreaker_tuple) for 5 cards. Higher tiebreaker wins."""
    if len(cards) != 5:
        raise ValueError("Need exactly 5 cards")
    ranks = [rank(c) for c in cards]
    suits_list = [suit(c) for c in cards]
    rank_counts = Counter(ranks)
    count_groups = sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0]))
    is_flush = len(set(suits_list)) == 1
    unique_ranks = sorted(set(ranks), reverse=True)

    def has_straight(rank_set):
        for high in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3]:  # 3 is lowest "high" for 3-4-5-6-7
            if all((high - k) % 13 in rank_set for k in range(5)):
                return high
        if {12, 0, 1, 2, 3}.issubset(rank_set):  # wheel A-2-3-4-5
            return 3  # 5-high
        return None

    straight_high = has_straight(set(ranks))

    tiebreaker = tuple(r for _, r in count_groups)  # e.g. (10, 10, 10, 5, 5) for full house
    kickers = tuple(sorted(ranks, key=lambda r: (rank_counts[r], r), reverse=True))

    if is_flush and straight_high is not None:
        return (STRAIGHT_FLUSH, (straight_high,))
    if count_groups[0][1] == 4:
        return (FOUR_KIND, tuple(r for r, _ in count_groups))
    if count_groups[0][1] == 3 and count_groups[1][1] >= 2:
        return (FULL_HOUSE, tuple(r for r, _ in count_groups))
    if is_flush:
        return (FLUSH, tuple(unique_ranks[:5]))
    if straight_high is not None:
        return (STRAIGHT, (straight_high,))
    if count_groups[0][1] == 3:
        return (THREE_KIND, tuple(r for r, _ in count_groups))
    if count_groups[0][1] == 2 and count_groups[1][1] == 2:
        return (TWO_PAIR, tuple(r for r, _ in count_groups))
    if count_groups[0][1] == 2:
        return (ONE_PAIR, tuple(r for r, _ in count_groups))
    return (HIGH_CARD, tuple(unique_ranks[:5]))


def evaluate_7(cards: List[int]) -> Tuple[int, Tuple[int, ...]]:
    """Best 5-card hand from 7 cards. Returns (hand_type, tiebreaker)."""
    if len(cards) != 7:
        raise ValueError("Need exactly 7 cards")
    best = None
    for five in combinations(cards, 5):
        t, tb = _evaluate_5(list(five))
        key = (t, tb)
        if best is None or key > best:
            best = key
    return best


def compare_hands(hand1: List[int], hand2: List[int]) -> int:
    """Compare two 7-card hands. Return 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
    v1 = evaluate_7(hand1)
    v2 = evaluate_7(hand2)
    if v1 > v2:
        return 1
    if v1 < v2:
        return -1
    return 0
