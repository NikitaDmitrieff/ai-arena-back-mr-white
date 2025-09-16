"""
Tournament management for Mister White games.
Handles running multiple games and collecting statistics.
"""

from typing import List, Tuple, Dict
from collections import defaultdict

import constants
from game import play_single_game


def run_tournament(
    num_games: int = 10,
    number_of_players: int = 5,
    models: List[Tuple[str, str]] = None,
    verbose: bool = False,
    show_progress: bool = True,
) -> Dict[str, any]:
    """Run multiple games and collect statistics across models."""

    # Use default models if none provided
    if models is None:
        models = constants.PROVIDERS_AND_MODELS

    results = []
    model_stats = defaultdict(lambda: {
        "games_played": 0,
        "games_as_mister_white": 0,
        "wins_as_mister_white": 0,
        "games_as_citizen": 0,
        "wins_as_citizen": 0,
        "total_wins": 0,
        "eliminated_count": 0,  # How often this model's player was eliminated
        "total_votes_received": 0,
    })

    print(f"🎮 Starting tournament with {num_games} games...")

    for game_num in range(num_games):
        if show_progress and (game_num + 1) % max(1, num_games // 10) == 0:
            print(f"Progress: {game_num + 1}/{num_games} games completed")

        # Play a single game
        result = play_single_game(
            game_id=game_num + 1,
            number_of_players=number_of_players,
            models=models,
            verbose=verbose,
            random_seed=game_num,  # Use game number as seed for reproducibility
        )
        results.append(result)

        # Update statistics for each player
        for player_info in result.players:
            model_key = f"{player_info['provider']}_{player_info['model']}"
            stats = model_stats[model_key]

            stats["games_played"] += 1
            stats["total_votes_received"] += player_info["votes_received"]

            if player_info["is_mister_white"]:
                stats["games_as_mister_white"] += 1
                if result.winner_side == "mister_white":
                    stats["wins_as_mister_white"] += 1
                    stats["total_wins"] += 1
            else:
                stats["games_as_citizen"] += 1
                if result.winner_side == "citizens":
                    stats["wins_as_citizen"] += 1
                    stats["total_wins"] += 1

            # Track eliminations
            if not player_info["survived"]:
                stats["eliminated_count"] += 1

    # Calculate additional metrics
    for model_key, stats in model_stats.items():
        games_played = stats["games_played"]
        if games_played > 0:
            stats["win_rate"] = stats["total_wins"] / games_played
            stats["survival_rate"] = (games_played - stats["eliminated_count"]) / games_played
            stats["avg_votes_received"] = stats["total_votes_received"] / games_played

            if stats["games_as_mister_white"] > 0:
                stats["mister_white_win_rate"] = (
                    stats["wins_as_mister_white"] / stats["games_as_mister_white"]
                )
            else:
                stats["mister_white_win_rate"] = 0.0

            if stats["games_as_citizen"] > 0:
                stats["citizen_win_rate"] = stats["wins_as_citizen"] / stats["games_as_citizen"]
            else:
                stats["citizen_win_rate"] = 0.0

    return {
        "results": results,
        "model_stats": dict(model_stats),
        "summary": {
            "total_games": num_games,
            "citizens_wins": sum(1 for r in results if r.winner_side == "citizens"),
            "mister_white_wins": sum(1 for r in results if r.winner_side == "mister_white"),
        },
    }
