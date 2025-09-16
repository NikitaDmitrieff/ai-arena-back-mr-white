"""
Main entry point for the Mister White AI tournament.
High-level orchestration of tournaments with CSV logging.
"""

from config import load_simulation_config
from tournament import run_tournament
from data_export import save_tournament_to_csv
from results import print_tournament_results


def main() -> None:
    """Main function to run the tournament with comprehensive CSV logging."""

    # Load all configuration from JSON
    enabled_models, folder_config, tournament_config = load_simulation_config()

    # Extract tournament parameters
    num_games = tournament_config.get("num_games", 2)
    verbose = tournament_config.get("verbose", False)
    show_progress = tournament_config.get("show_progress", True)

    # Number of players = number of enabled models
    number_of_players = len(enabled_models)

    print(f"🚀 Starting Mister White AI Tournament")
    print(f"📊 Configuration: {num_games} games, {number_of_players} players")
    print(f"🤖 Models: {len(enabled_models)} enabled models (one per player)")

    # Show custom folder naming if configured
    if folder_config.get("custom_folder_name") or folder_config.get("folder_suffix"):
        print(f"📁 Custom folder naming enabled")

    # Run the tournament
    tournament_data = run_tournament(
        num_games=num_games,
        models=enabled_models,
        verbose=verbose,
        show_progress=show_progress,
    )

    # Save comprehensive data to CSV files (including partial results if tournament failed)
    folder_name = save_tournament_to_csv(
        tournament_data=tournament_data,
        folder_config=folder_config,
    )

    # Print results to console
    print_tournament_results(tournament_data)

    # Show sample games
    print("\n" + "🎲 SAMPLE GAMES".center(80))
    print("-" * 80)
    for i, result in enumerate(tournament_data["results"][:3]):  # Show first 3 games
        print(f"\nGame {i+1}: {result.winner_side.title()} Win")
        print(f"  Secret Word: {result.secret_word}")
        print(
            f"  Mister White: {result.mister_white_player} ({result.mister_white_model[0]}/{result.mister_white_model[1]})"
        )
        print(
            f"  Eliminated: {result.eliminated_player} ({result.eliminated_model[0]}/{result.eliminated_model[1]})"
        )
        print(f"  Vote Counts: {result.vote_counts}")

    print(f"\n✅ Tournament complete! Data saved in folder: {folder_name}")


if __name__ == "__main__":
    main()
