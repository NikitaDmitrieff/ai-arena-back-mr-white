"""
Data export functionality for Mister White tournaments.
Handles CSV export with organized folder structure.
"""

import csv
import os
from datetime import datetime
from typing import Dict


def save_tournament_to_csv(
    tournament_data: Dict[str, any],
    folder_config: Dict[str, any] = None,
) -> str:
    """Save comprehensive tournament data to CSV files in organized subfolders."""

    if folder_config is None:
        folder_config = {}

    # Extract tournament summary info
    summary = tournament_data["summary"]
    completed_games = summary.get('completed_games', summary.get('total_games', 0))
    planned_games = summary.get('planned_games', completed_games)
    failed_game = summary.get('failed_game')

    # Count models used in this tournament
    openai_models = set()
    mistral_models = set()

    for model_key in tournament_data["model_stats"].keys():
        provider, model = model_key.split("_", 1)
        if provider == "openai":
            openai_models.add(model)
        elif provider == "mistral":
            mistral_models.add(model)

    # Derive number of players from total models used
    number_of_players = len(openai_models) + len(mistral_models)

    # Generate timestamp and folder structure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    datetime_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    model_counts = f"{len(openai_models)}o_{len(mistral_models)}m"

    # Create folder name based on configuration
    if folder_config.get("use_custom_only", False) and folder_config.get("custom_folder_name"):
        folder_name = folder_config["custom_folder_name"]
    elif folder_config.get("custom_folder_name"):
        folder_name = folder_config["custom_folder_name"]
    else:
        # Default naming - use completed games and add partial indicator if needed
        games_label = f"{completed_games}games"
        if failed_game is not None:
            games_label += f"_partial"
        folder_name = f"{datetime_str}_{games_label}_{number_of_players}players_{model_counts}"

        # Add suffix if specified
        if folder_config.get("folder_suffix"):
            folder_name += folder_config["folder_suffix"]

    filename_base = f"{completed_games}games_{number_of_players}players_{timestamp}"
    if failed_game is not None:
        filename_base += "_partial"

    # Create the organized results directory structure
    base_results_dir = "/Users/nikitadmitrieff/Desktop/Projects/coding/L/Mister white AI/results"
    results_dir = os.path.join(base_results_dir, folder_name)
    os.makedirs(results_dir, exist_ok=True)

    # Create CSV files: games summary, detailed player data, messages, and model stats

    # 1. Games Summary CSV
    games_csv_path = os.path.join(results_dir, f"{filename_base}_games.csv")
    with open(games_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id", "timestamp", "secret_word", "winner_side",
            "mister_white_player", "mister_white_provider", "mister_white_model",
            "eliminated_player", "eliminated_provider", "eliminated_model",
            "total_votes_cast", "vote_counts_json",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in tournament_data["results"]:
            writer.writerow({
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
            })

    # 2. Detailed Player Data CSV
    players_csv_path = os.path.join(results_dir, f"{filename_base}_players.csv")
    with open(players_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id", "player_name", "provider", "model",
            "is_mister_white", "word", "survived", "votes_received",
            "won_game", "secret_word", "winner_side",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in tournament_data["results"]:
            for player in result.players:
                won_game = (
                    (player["is_mister_white"] and result.winner_side == "mister_white") or
                    (not player["is_mister_white"] and result.winner_side == "citizens")
                )
                writer.writerow({
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
                })

    # 3. Messages CSV
    messages_csv_path = os.path.join(results_dir, f"{filename_base}_messages.csv")
    with open(messages_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "game_id", "player_name", "message_type", "phase", "round",
            "content", "secret_word", "is_mister_white",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in tournament_data["results"]:
            # Create a lookup for player info
            player_lookup = {p["name"]: p for p in result.players}

            for message in result.messages:
                player_info = player_lookup.get(message["player"], {})
                writer.writerow({
                    "game_id": result.game_id,
                    "player_name": message["player"],
                    "message_type": message["type"],
                    "phase": message["phase"],
                    "round": message["round"],
                    "content": message["content"],
                    "secret_word": result.secret_word,
                    "is_mister_white": player_info.get("is_mister_white", False),
                })

    # 4. Model Statistics CSV
    stats_csv_path = os.path.join(results_dir, f"{filename_base}_model_stats.csv")
    with open(stats_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "provider", "model", "games_played", "total_wins", "win_rate",
            "games_as_mister_white", "wins_as_mister_white", "mister_white_win_rate",
            "games_as_citizen", "wins_as_citizen", "citizen_win_rate",
            "eliminated_count", "survival_rate", "avg_votes_received",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for model_key, stats in tournament_data["model_stats"].items():
            provider, model = model_key.split("_", 1)
            writer.writerow({
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
            })

    # 5. Tournament Summary CSV (includes failure information)
    tournament_csv_path = os.path.join(results_dir, f"{filename_base}_tournament_summary.csv")
    with open(tournament_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "planned_games", "completed_games", "failed_game", "success_rate",
            "citizens_wins", "mister_white_wins", "tournament_status",
            "total_models", "openai_models", "mistral_models", 
            "export_timestamp"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerow({
            "planned_games": planned_games,
            "completed_games": completed_games,
            "failed_game": failed_game,
            "success_rate": summary.get('success_rate', 0),
            "citizens_wins": summary["citizens_wins"],
            "mister_white_wins": summary["mister_white_wins"],
            "tournament_status": "PARTIAL" if failed_game is not None else "COMPLETE",
            "total_models": number_of_players,
            "openai_models": len(openai_models),
            "mistral_models": len(mistral_models),
            "export_timestamp": timestamp
        })

    print(f"\n📊 CSV files saved in organized folder: {folder_name}")
    status_indicator = "⚠️ PARTIAL" if failed_game is not None else "✅ COMPLETE"
    print(f"  Status: {status_indicator} ({completed_games}/{planned_games} games)")
    print(f"  • Games: {os.path.basename(games_csv_path)}")
    print(f"  • Players: {os.path.basename(players_csv_path)}")
    print(f"  • Messages: {os.path.basename(messages_csv_path)}")
    print(f"  • Model Stats: {os.path.basename(stats_csv_path)}")
    print(f"  • Tournament Summary: {os.path.basename(tournament_csv_path)}")
    print(f"  • Full path: {results_dir}")

    return folder_name
