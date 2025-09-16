"""
Results display and analysis for Mister White tournaments.
Handles console output of tournament statistics and rankings.
"""

from typing import Dict


def print_tournament_results(tournament_data: Dict[str, any]) -> None:
    """Print detailed tournament results and rankings."""

    model_stats = tournament_data["model_stats"]
    summary = tournament_data["summary"]

    print("\n" + "=" * 80)
    print("🏆 TOURNAMENT RESULTS")
    print("=" * 80)

    # Handle both old format (total_games) and new format (completed_games) for compatibility
    completed_games = summary.get("completed_games", summary.get("total_games", 0))
    planned_games = summary.get("planned_games", completed_games)

    if summary.get("failed_game") is not None:
        print(f"\n⚠️  Tournament Status: PARTIAL COMPLETION")
        print(
            f"Completed Games: {completed_games}/{planned_games} ({summary.get('success_rate', 0)*100:.1f}%)"
        )
        print(f"Failed at Game: {summary['failed_game']}")
    else:
        print(f"\n✅ Tournament Status: COMPLETED SUCCESSFULLY")
        print(f"Games Played: {completed_games}")

    if completed_games > 0:
        print(
            f"Citizens Wins: {summary['citizens_wins']} ({summary['citizens_wins']/completed_games*100:.1f}%)"
        )
        print(
            f"Mister White Wins: {summary['mister_white_wins']} ({summary['mister_white_wins']/completed_games*100:.1f}%)"
        )
    else:
        print("No games completed successfully.")

    # Sort models by overall win rate
    sorted_models = sorted(
        model_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True
    )

    print("\n" + "🥇 MODEL RANKINGS (by overall win rate)".center(80))
    print("-" * 80)
    print(
        f"{'Rank':<4} {'Model':<25} {'Win Rate':<10} {'Games':<6} {'MW Rate':<8} {'Cit Rate':<9} {'Survival':<9}"
    )
    print("-" * 80)

    for rank, (model_key, stats) in enumerate(sorted_models, 1):
        provider, model = model_key.split("_", 1)
        model_display = f"{provider}/{model}"
        if len(model_display) > 24:
            model_display = model_display[:21] + "..."

        print(
            f"{rank:<4} {model_display:<25} "
            f"{stats['win_rate']:.1%}      "
            f"{stats['games_played']:<6} "
            f"{stats['mister_white_win_rate']:.1%}     "
            f"{stats['citizen_win_rate']:.1%}      "
            f"{stats['survival_rate']:.1%}"
        )

    print("\n" + "📊 DETAILED STATISTICS".center(80))
    print("-" * 80)

    for model_key, stats in sorted_models:
        provider, model = model_key.split("_", 1)
        print(f"\n{provider}/{model}:")
        print(f"  • Total Games: {stats['games_played']}")
        print(f"  • Overall Wins: {stats['total_wins']} ({stats['win_rate']:.1%})")
        print(
            f"  • As Mister White: {stats['wins_as_mister_white']}/{stats['games_as_mister_white']} ({stats['mister_white_win_rate']:.1%})"
        )
        print(
            f"  • As Citizen: {stats['wins_as_citizen']}/{stats['games_as_citizen']} ({stats['citizen_win_rate']:.1%})"
        )
        print(
            f"  • Times Eliminated: {stats['eliminated_count']} (Survival: {stats['survival_rate']:.1%})"
        )
        print(f"  • Avg Votes Received: {stats['avg_votes_received']:.1f}")
