"""
Tournament management for Mister White games.
Handles running multiple games and collecting statistics.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from src.config import constants
from src.core.game import play_single_game
from src.data.data_export import append_game_to_csv, initialize_csv_files


def run_tournament(
    num_games: int = 10,
    models: List[Tuple[str, str]] = None,
    verbose: bool = False,
    show_progress: bool = True,
    folder_config: Dict[str, any] = None,
) -> Dict[str, any]:
    """Run multiple games and collect statistics across models."""

    # Use default models if none provided
    if models is None:
        models = constants.PROVIDERS_AND_MODELS

    # Number of players is determined by number of models
    number_of_players = len(models)

    # Initialize CSV files for incremental writing
    if folder_config is None:
        folder_config = {}

    results_dir, filename_base = initialize_csv_files(
        enabled_models=models, folder_config=folder_config, num_games=num_games
    )

    print(f"📊 CSV files initialized: {results_dir}")

    results = []  # Keep minimal results for final stats processing
    model_stats = defaultdict(
        lambda: {
            "games_played": 0,
            "games_as_mister_white": 0,
            "wins_as_mister_white": 0,
            "games_as_citizen": 0,
            "wins_as_citizen": 0,
            "total_wins": 0,
            "eliminated_count": 0,  # How often this model's player was eliminated
            "total_votes_received": 0,
        }
    )

    print(f"🎮 Starting tournament with {num_games} games...")

    completed_games = 0
    failed_game = None

    for game_num in range(num_games):
        if show_progress and (game_num + 1) % max(1, num_games // 10) == 0:
            print(f"Progress: {game_num + 1}/{num_games} games completed")

        try:
            # Play a single game
            result = play_single_game(
                game_id=game_num + 1,
                models=models,
                verbose=verbose,
                random_seed=game_num,  # Use game number as seed for reproducibility
            )

            # Immediately write this game's data to CSV files
            append_game_to_csv(result, results_dir, filename_base)

            # Keep minimal result data for final summary
            results.append(result)
            completed_games = game_num + 1

        except Exception as e:
            failed_game = game_num + 1
            print(f"\n⚠️  ERROR: Game {failed_game} failed with error: {str(e)}")
            print(f"💾 Game data written incrementally. {completed_games} games saved.")
            if verbose:
                print(f"   Error details: {type(e).__name__}: {str(e)}")
            break

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
            stats["survival_rate"] = (
                games_played - stats["eliminated_count"]
            ) / games_played
            stats["avg_votes_received"] = stats["total_votes_received"] / games_played

            if stats["games_as_mister_white"] > 0:
                stats["mister_white_win_rate"] = (
                    stats["wins_as_mister_white"] / stats["games_as_mister_white"]
                )
            else:
                stats["mister_white_win_rate"] = 0.0

            if stats["games_as_citizen"] > 0:
                stats["citizen_win_rate"] = (
                    stats["wins_as_citizen"] / stats["games_as_citizen"]
                )
            else:
                stats["citizen_win_rate"] = 0.0

    # Final status report
    if completed_games < num_games:
        print(
            f"🛑 Tournament stopped early after {completed_games}/{num_games} games due to error in game {failed_game}"
        )
    else:
        print(
            f"✅ Tournament completed successfully: {completed_games}/{num_games} games"
        )

    return {
        "results": results,
        "model_stats": dict(model_stats),
        "csv_info": {
            "results_dir": results_dir,
            "filename_base": filename_base,
        },
        "summary": {
            "planned_games": num_games,
            "completed_games": completed_games,
            "failed_game": failed_game,
            "success_rate": completed_games / num_games if num_games > 0 else 0,
            "citizens_wins": sum(1 for r in results if r.winner_side == "citizens"),
            "mister_white_wins": sum(
                1 for r in results if r.winner_side == "mister_white"
            ),
        },
    }
