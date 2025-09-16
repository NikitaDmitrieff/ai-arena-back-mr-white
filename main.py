"""
Main entry point for the Mister White AI tournament.
High-level orchestration of tournaments with CSV logging.
"""

from utils import run_tournament, print_tournament_results, save_tournament_to_csv


def main() -> None:
    """Main function to run the tournament with comprehensive CSV logging."""
    
    # Tournament configuration
    num_games = 5
    number_of_players = 5
    verbose = False  # Set to True to see individual game details
    show_progress = True
    
    print(f"🚀 Starting Mister White AI Tournament")
    print(f"📊 Configuration: {num_games} games, {number_of_players} players")
    
    # Run the tournament
    tournament_data = run_tournament(
        num_games=num_games,
        number_of_players=number_of_players,
        verbose=verbose,
        show_progress=show_progress
    )
    
    # Save comprehensive data to CSV files
    filename_base = save_tournament_to_csv(
        tournament_data=tournament_data,
        num_games=num_games,
        number_of_players=number_of_players
    )
    
    # Print results to console
    print_tournament_results(tournament_data)
    
    # Show sample games
    print("\n" + "🎲 SAMPLE GAMES".center(80))
    print("-" * 80)
    for i, result in enumerate(tournament_data["results"][:3]):  # Show first 3 games
        print(f"\nGame {i+1}: {result.winner_side.title()} Win")
        print(f"  Secret Word: {result.secret_word}")
        print(f"  Mister White: {result.mister_white_player} ({result.mister_white_model[0]}/{result.mister_white_model[1]})")
        print(f"  Eliminated: {result.eliminated_player} ({result.eliminated_model[0]}/{result.eliminated_model[1]})")
        print(f"  Vote Counts: {result.vote_counts}")
    
    print(f"\n✅ Tournament complete! Data saved with prefix: {filename_base}")


if __name__ == "__main__":
    main()
