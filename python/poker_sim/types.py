"""Shared types for the simulation package."""


class SimResult:
    """Result of a Monte Carlo simulation run."""

    __slots__ = ("wins", "ties", "losses", "total")

    def __init__(self, wins: int, ties: int, total: int, losses: int = 0):
        self.wins = wins
        self.ties = ties
        self.losses = losses if losses else (total - wins - ties)
        self.total = total

    def win_rate(self) -> float:
        return self.wins / self.total if self.total else 0.0

    def tie_rate(self) -> float:
        return self.ties / self.total if self.total else 0.0

    def loss_rate(self) -> float:
        return self.losses / self.total if self.total else 0.0
