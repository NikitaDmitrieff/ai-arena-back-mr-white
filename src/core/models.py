"""
Data models and structures for the Mister White game.
Contains all data types used across the game system.
"""

from typing import Dict, List, NamedTuple, Tuple


class GameResult(NamedTuple):
    """Structured result from a single game."""

    game_id: int
    timestamp: str
    winner_side: str  # "citizens" or "mister_white"
    mister_white_player: str
    mister_white_model: Tuple[str, str]  # (provider, model)
    eliminated_player: str
    eliminated_model: Tuple[str, str]  # (provider, model)
    secret_word: str
    vote_counts: Dict[str, int]
    players: List[Dict[str, any]]  # List of player info with their models
    messages: List[Dict[str, str]]  # All game messages
