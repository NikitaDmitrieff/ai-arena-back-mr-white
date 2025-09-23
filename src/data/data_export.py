"""
Data export functionality for Mister White tournaments.
Handles CSV export with organized folder structure.
"""

import csv
import os
from datetime import datetime
from typing import Dict, Tuple


def initialize_csv_files(
    enabled_models: list, folder_config: Dict[str, any] = None, num_games: int = 0
) -> Tuple[str, str]:
    """Initialize CSV files with headers for incremental writing.

    Returns: (results_dir, filename_base) for use in append_game_to_csv
    """
    if folder_config is None:
        folder_config = {}

    # Count models
    openai_models = set()
    mistral_models = set()
    for provider, model in enabled_models:
        if provider == "openai":
            openai_models.add(model)
        elif provider == "mistral":
            mistral_models.add(model)

    number_of_players = len(enabled_models)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    datetime_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    model_counts = f"{len(openai_models)}o_{len(mistral_models)}m"

    # Create folder name based on configuration
    if folder_config.get("use_custom_only", False) and folder_config.get(
        "custom_folder_name"
    ):
        folder_name = folder_config["custom_folder_name"]
    elif folder_config.get("custom_folder_name"):
        folder_name = folder_config["custom_folder_name"]
    else:
        folder_name = (
            f"{datetime_str}_{num_games}games_{number_of_players}players_{model_counts}"
        )
        if folder_config.get("folder_suffix"):
            folder_name += folder_config["folder_suffix"]

    filename_base = f"{num_games}games_{number_of_players}players_{timestamp}"

    # Create results directory
    base_results_dir = (
        "/Users/nikitadmitrieff/Desktop/Projects/coding/L/Mister white AI/results"
    )
    results_dir = os.path.join(base_results_dir, folder_name)
    os.makedirs(results_dir, exist_ok=True)

    # Initialize CSV files with headers
    # 1. Games CSV
    games_csv_path = os.path.join(results_dir, f"{filename_base}_games.csv")
    with open(games_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "timestamp",
            "secret_word",
            "winner_side",
            "mister_white_player",
            "mister_white_provider",
            "mister_white_model",
            "eliminated_player",
            "eliminated_provider",
            "eliminated_model",
            "total_votes_cast",
            "vote_counts_json",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # 2. Players CSV
    players_csv_path = os.path.join(results_dir, f"{filename_base}_players.csv")
    with open(players_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "player_name",
            "provider",
            "model",
            "is_mister_white",
            "word",
            "survived",
            "votes_received",
            "won_game",
            "secret_word",
            "winner_side",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # 3. Messages CSV
    messages_csv_path = os.path.join(results_dir, f"{filename_base}_messages.csv")
    with open(messages_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "provider",
            "model",
            "player_name",
            "message_type",
            "phase",
            "round",
            "content",
            "secret_word",
            "is_mister_white",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    return results_dir, filename_base


def append_game_to_csv(result, results_dir: str, filename_base: str) -> None:
    """Append a single game's results to the CSV files."""

    # 1. Append to Games CSV
    games_csv_path = os.path.join(results_dir, f"{filename_base}_games.csv")
    with open(games_csv_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "timestamp",
            "secret_word",
            "winner_side",
            "mister_white_player",
            "mister_white_provider",
            "mister_white_model",
            "eliminated_player",
            "eliminated_provider",
            "eliminated_model",
            "total_votes_cast",
            "vote_counts_json",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(
            {
                "game_id": result.game_id,
                "timestamp": result.timestamp,
                "secret_word": result.secret_word,
                "winner_side": result.winner_side,
                "mister_white_player": result.mister_white_player,
                "mister_white_provider": result.mister_white_model[0],
                "mister_white_model": result.mister_white_model[1],
                "eliminated_player": result.eliminated_player,
                "eliminated_provider": result.eliminated_model[0],
                "eliminated_model": result.eliminated_model[1],
                "total_votes_cast": sum(result.vote_counts.values()),
                "vote_counts_json": str(result.vote_counts),
            }
        )

    # 2. Append to Players CSV
    players_csv_path = os.path.join(results_dir, f"{filename_base}_players.csv")
    with open(players_csv_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "player_name",
            "provider",
            "model",
            "is_mister_white",
            "word",
            "survived",
            "votes_received",
            "won_game",
            "secret_word",
            "winner_side",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for player in result.players:
            won_game = (
                player["is_mister_white"] and result.winner_side == "mister_white"
            ) or (not player["is_mister_white"] and result.winner_side == "citizens")
            writer.writerow(
                {
                    "game_id": result.game_id,
                    "player_name": player["name"],
                    "provider": player["provider"],
                    "model": player["model"],
                    "is_mister_white": player["is_mister_white"],
                    "word": player["word"],
                    "survived": player["survived"],
                    "votes_received": player["votes_received"],
                    "won_game": won_game,
                    "secret_word": result.secret_word,
                    "winner_side": result.winner_side,
                }
            )

    # 3. Append to Messages CSV
    messages_csv_path = os.path.join(results_dir, f"{filename_base}_messages.csv")
    with open(messages_csv_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id",
            "provider",
            "model",
            "player_name",
            "message_type",
            "phase",
            "round",
            "content",
            "secret_word",
            "is_mister_white",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Create a lookup for player info
        player_lookup = {p["name"]: p for p in result.players}

        for message in result.messages:
            player_info = player_lookup.get(message["player"], {})
            writer.writerow(
                {
                    "game_id": result.game_id,
                    "provider": player_info.get("provider", "unknown"),
                    "model": player_info.get("model", "unknown"),
                    "player_name": message["player"],
                    "message_type": message["type"],
                    "phase": message["phase"],
                    "round": message["round"],
                    "content": message["content"],
                    "secret_word": result.secret_word,
                    "is_mister_white": player_info.get("is_mister_white", False),
                }
            )


def finalize_tournament_csv(
    tournament_data: Dict[str, any],
    results_dir: str,
    filename_base: str,
) -> str:
    """Write final tournament summary and model statistics CSV files."""

    summary = tournament_data["summary"]
    completed_games = summary.get("completed_games", summary.get("total_games", 0))
    planned_games = summary.get("planned_games", completed_games)
    failed_game = summary.get("failed_game")

    # Count models used in this tournament
    openai_models = set()
    mistral_models = set()

    for model_key in tournament_data["model_stats"].keys():
        provider, model = model_key.split("_", 1)
        if provider == "openai":
            openai_models.add(model)
        elif provider == "mistral":
            mistral_models.add(model)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Update filename if partial
    final_filename_base = filename_base
    if failed_game is not None and "_partial" not in filename_base:
        final_filename_base += "_partial"

    # 1. Model Statistics CSV
    stats_csv_path = os.path.join(results_dir, f"{final_filename_base}_model_stats.csv")
    with open(stats_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "provider",
            "model",
            "games_played",
            "total_wins",
            "win_rate",
            "games_as_mister_white",
            "wins_as_mister_white",
            "mister_white_win_rate",
            "games_as_citizen",
            "wins_as_citizen",
            "citizen_win_rate",
            "eliminated_count",
            "survival_rate",
            "avg_votes_received",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for model_key, stats in tournament_data["model_stats"].items():
            provider, model = model_key.split("_", 1)
            writer.writerow(
                {
                    "provider": provider,
                    "model": model,
                    "games_played": stats["games_played"],
                    "total_wins": stats["total_wins"],
                    "win_rate": stats["win_rate"],
                    "games_as_mister_white": stats["games_as_mister_white"],
                    "wins_as_mister_white": stats["wins_as_mister_white"],
                    "mister_white_win_rate": stats["mister_white_win_rate"],
                    "games_as_citizen": stats["games_as_citizen"],
                    "wins_as_citizen": stats["wins_as_citizen"],
                    "citizen_win_rate": stats["citizen_win_rate"],
                    "eliminated_count": stats["eliminated_count"],
                    "survival_rate": stats["survival_rate"],
                    "avg_votes_received": stats["avg_votes_received"],
                }
            )

    # 2. Tournament Summary CSV
    tournament_csv_path = os.path.join(
        results_dir, f"{final_filename_base}_tournament_summary.csv"
    )
    with open(tournament_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "planned_games",
            "completed_games",
            "failed_game",
            "success_rate",
            "citizens_wins",
            "mister_white_wins",
            "tournament_status",
            "total_models",
            "openai_models",
            "mistral_models",
            "export_timestamp",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerow(
            {
                "planned_games": planned_games,
                "completed_games": completed_games,
                "failed_game": failed_game,
                "success_rate": summary.get("success_rate", 0),
                "citizens_wins": summary["citizens_wins"],
                "mister_white_wins": summary["mister_white_wins"],
                "tournament_status": (
                    "PARTIAL" if failed_game is not None else "COMPLETE"
                ),
                "total_models": len(openai_models) + len(mistral_models),
                "openai_models": len(openai_models),
                "mistral_models": len(mistral_models),
                "export_timestamp": timestamp,
            }
        )

    folder_name = os.path.basename(results_dir)
    status_indicator = "⚠️ PARTIAL" if failed_game is not None else "✅ COMPLETE"
    print(f"  Status: {status_indicator} ({completed_games}/{planned_games} games)")
    print(f"  • Model Stats: {os.path.basename(stats_csv_path)}")
    print(f"  • Tournament Summary: {os.path.basename(tournament_csv_path)}")

    return folder_name
