"""
Utilities for the Mister White game.
Contains game logic, CSV logging, and analysis functions.
"""

from __future__ import annotations

import csv
import json
import os
import random
from datetime import datetime
from typing import List, Optional, Dict, Tuple, NamedTuple
from collections import defaultdict

import constants
import prompts
from agent import Player


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


class MisterWhiteGame:
    """Very simple groundwork for a Mister White style game.

    This class provides only the minimal building blocks:
    - add players
    - set the secret word
    - assign roles (one Mister White, others get the word)
    - expose a per-player view of their role/word

    Game rounds, clues, voting, and scoring are intentionally omitted
    to keep this setup minimal.
    """

    def __init__(self) -> None:
        self.players: List[Player] = []
        self.secret_word: Optional[str] = None
        self._started: bool = False
        self._mister_white_index: Optional[int] = None
        self.messages: List[Dict[str, str]] = []

    # Setup API
    def add_player(self, name: str, provider: str = "openai", model: str = "gpt-4o-mini") -> Player:
        player = Player(
            name=name.strip(),
            description=f"AI player named {name.strip()}",
            provider=provider,
            model=model
        )
        self.players.append(player)
        return self.players[-1]

    def set_secret_word(self, word: str) -> None:
        word = (word or "").strip()
        self.secret_word = word

    # Lifecycle
    def start(self, *, random_seed: Optional[int] = None) -> None:
        self._assign_roles(random_seed=random_seed)
        self._started = True

    def reset(self) -> None:
        self.players.clear()
        self.secret_word = None
        self._started = False
        self._mister_white_index = None
        self.messages.clear()

    # Views / Queries
    def get_player_view(self, player_name: str) -> str:
        player = self._find_player(player_name)
        if player.is_mister_white:
            return "You are Mister White. You do NOT know the secret word."
        return f"Your secret word is: {player.word}"

    # Internals
    def _assign_roles(self, *, random_seed: Optional[int] = None) -> None:
        if random_seed is not None:
            random.seed(random_seed)
        self._mister_white_index = random.randrange(len(self.players))
        for idx, player in enumerate(self.players):
            is_white = idx == self._mister_white_index
            player.is_mister_white = is_white
            player.word = None if is_white else self.secret_word

    def _find_player(self, player_name: str) -> Player:
        name_norm = player_name.strip().lower()
        for p in self.players:
            if p.name.lower() == name_norm:
                return p
        raise ValueError(f"Player '{player_name}' not found")


def load_model_config(config_path: str = "model_config.json") -> Tuple[List[Tuple[str, str]], Dict[str, any]]:
    """Load model configuration and folder naming options from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Convert enabled models to the format expected by the game
        enabled_models = []
        for model_config in config.get("enabled_models", []):
            enabled_models.append((model_config["provider"], model_config["model"]))
        
        if not enabled_models:
            print("⚠️  No enabled models found in config, falling back to constants")
            enabled_models = constants.PROVIDERS_AND_MODELS
        else:
            print(f"📋 Loaded {len(enabled_models)} enabled models from {config_path}")
        
        # Load folder naming configuration
        folder_config = config.get("folder_naming", {
            "custom_folder_name": None,
            "folder_suffix": None,
            "use_custom_only": False
        })
        
        return enabled_models, folder_config
        
    except FileNotFoundError:
        print(f"⚠️  Config file {config_path} not found, using constants")
        return constants.PROVIDERS_AND_MODELS, {}
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON in {config_path}, using constants")
        return constants.PROVIDERS_AND_MODELS, {}


def play_single_game(
    game_id: int,
    number_of_players: int = 5, 
    names: List[str] = None, 
    words: List[str] = None, 
    models: List[Tuple[str, str]] = None, 
    verbose: bool = True,
    random_seed: Optional[int] = None
) -> GameResult:
    """Play a single game and return structured results."""
    
    timestamp = datetime.now().isoformat()
    
    # Use defaults if not provided
    if names is None:
        names = constants.NAMES
    if words is None:
        words = constants.SECRET_WORD
    if models is None:
        models = constants.PROVIDERS_AND_MODELS

    # Initialize and start the game
    if random_seed is not None:
        random.seed(random_seed)
        
    game = MisterWhiteGame()
    for i in range(number_of_players):
        name = names[i]
        # Cycle through available models for variety
        provider, model = models[i % len(models)]
        game.add_player(name=name, provider=provider, model=model)
    
    selected_word = random.choice(words)
    game.set_secret_word(selected_word)
    game.start(random_seed=random_seed)

    if verbose:
        for p in game.players:
            print(f"- {p.name}: {game.get_player_view(p.name)}")

    ### Record all the messages within game
    # 1. Query each agent for their word
    if verbose:
        print("\n=== WORD PHASE ===")
    
    # First, let non-Mister White players give their clues
    for player in game.players:
        if not player.is_mister_white:
            system_prompt = prompts.REGULAR_PLAYER_CLUE_SYSTEM.format(word=player.word)
            user_prompt = prompts.REGULAR_PLAYER_CLUE_USER.format(word=player.word)
            
            clue = player.invoke(user_prompt, system_prompt)
            game.messages.append({
                "player": player.name, 
                "type": "clue", 
                "content": clue, 
                "round": 0,
                "phase": "clue"
            })
            if verbose:
                print(f"{player.name}: {clue}")
    
    # Then, let Mister White give their clue after seeing others' clues
    mister_white = next(p for p in game.players if p.is_mister_white)
    if game.messages:  # If there are previous clues
        previous_clues = "\n".join([f"{msg['player']}: {msg['content']}" for msg in game.messages if msg['type'] == 'clue'])
        system_prompt = prompts.MISTER_WHITE_CLUE_WITH_CONTEXT_SYSTEM
        user_prompt = prompts.MISTER_WHITE_CLUE_WITH_CONTEXT_USER.format(previous_clues=previous_clues)
    else:
        system_prompt = prompts.MISTER_WHITE_CLUE_NO_CONTEXT_SYSTEM
        user_prompt = prompts.MISTER_WHITE_CLUE_NO_CONTEXT_USER
    
    clue = mister_white.invoke(user_prompt, system_prompt)
    game.messages.append({
        "player": mister_white.name, 
        "type": "clue", 
        "content": clue, 
        "round": 0,
        "phase": "clue"
    })
    if verbose:
        print(f"{mister_white.name}: {clue}")

    # 2. Killing round
    if verbose:
        print("\n=== KILLING ROUND ===")
        print("\n--- Discussion Phase (2 rounds) ---")
    
    for round_num in range(1, 3):
        if verbose:
            print(f"\nRound {round_num}:")
        for player in game.players:
            # Build context of all previous messages
            context = "\n".join([f"{msg['player']}: {msg['content']}" for msg in game.messages if msg['type'] in ['clue', 'discussion']])
            
            system_prompt = prompts.DISCUSSION_SYSTEM.format(player_name=player.name)
            if player.is_mister_white:
                user_prompt = prompts.MISTER_WHITE_DISCUSSION_USER.format(context=context)
            else:
                user_prompt = prompts.REGULAR_PLAYER_DISCUSSION_USER.format(context=context, word=player.word)
            
            response = player.invoke(user_prompt, system_prompt)
            game.messages.append({
                "player": player.name, 
                "type": "discussion", 
                "content": response, 
                "round": round_num,
                "phase": "discussion"
            })
            if verbose:
                print(f"{player.name}: {response}")

    #    b. Each agent gets one chance to vote
    if verbose:
        print("\n--- Voting Phase ---")
    votes = {}
    for player in game.players:
        # Build context of all messages
        context = "\n".join([f"{msg['player']}: {msg['content']}" for msg in game.messages])
        
        system_prompt = prompts.VOTING_SYSTEM.format(player_name=player.name)
        user_prompt = prompts.VOTING_USER.format(context=context)
        
        vote = player.invoke(user_prompt, system_prompt).strip()
        game.messages.append({
            "player": player.name, 
            "type": "vote", 
            "content": vote, 
            "round": 1,
            "phase": "voting"
        })
        votes[player.name] = vote
        if verbose:
            print(f"{player.name} votes for: {vote}")

    # Count votes and determine result
    vote_counts = {}
    for voter, voted_for in votes.items():
        vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1
    
    # Find player with most votes
    eliminated = max(vote_counts.items(), key=lambda x: x[1])[0] if vote_counts else ""
    eliminated_player = None
    for p in game.players:
        if p.name.lower() == eliminated.lower():
            eliminated_player = p
            break
    
    # Determine winner
    mister_white_player = next(p for p in game.players if p.is_mister_white)
    winner_side = "citizens" if eliminated_player and eliminated_player.is_mister_white else "mister_white"
    
    if verbose:
        print("\n=== GAME RESULTS ===")
        print(f"Vote results: {vote_counts}")
        print(f"Eliminated: {eliminated}")
        
        if winner_side == "citizens":
            print("🎉 Citizens win! Mister White was caught!")
        else:
            print(f"💀 Mister White ({mister_white_player.name}) wins! An innocent was eliminated.")
        
        print(f"\nThe secret word was: {game.secret_word}")
        print(f"Mister White was: {mister_white_player.name}")
    
    # Get model info for players
    player_models = {}
    for i, player in enumerate(game.players):
        provider, model = models[i % len(models)]
        player_models[player.name] = (provider, model)
    
    # Create detailed player info
    players_info = []
    for player in game.players:
        provider, model = player_models[player.name]
        players_info.append({
            "name": player.name,
            "provider": provider,
            "model": model,
            "is_mister_white": player.is_mister_white,
            "word": player.word,
            "survived": player.name != eliminated,
            "votes_received": vote_counts.get(player.name, 0)
        })
    
    return GameResult(
        game_id=game_id,
        timestamp=timestamp,
        winner_side=winner_side,
        mister_white_player=mister_white_player.name,
        mister_white_model=player_models[mister_white_player.name],
        eliminated_player=eliminated,
        eliminated_model=player_models.get(eliminated, ("unknown", "unknown")),
        secret_word=selected_word,
        vote_counts=vote_counts,
        players=players_info,
        messages=game.messages
    )


def run_tournament(
    num_games: int = 10,
    number_of_players: int = 5,
    models: List[Tuple[str, str]] = None,
    verbose: bool = False,
    show_progress: bool = True
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
        "total_votes_received": 0
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
            random_seed=game_num  # Use game number as seed for reproducibility
        )
        results.append(result)
        
        # Update statistics for each player
        for player_info in result.players:
            model_key = f"{player_info['provider']}_{player_info['model']}"
            stats = model_stats[model_key]
            
            stats["games_played"] += 1
            stats["total_votes_received"] += player_info['votes_received']
            
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
                stats["mister_white_win_rate"] = stats["wins_as_mister_white"] / stats["games_as_mister_white"]
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
            "mister_white_wins": sum(1 for r in results if r.winner_side == "mister_white")
        }
    }


def save_tournament_to_csv(tournament_data: Dict[str, any], num_games: int, number_of_players: int, folder_config: Dict[str, any] = None) -> str:
    """Save comprehensive tournament data to CSV files in organized subfolders."""
    
    if folder_config is None:
        folder_config = {}
    
    # Count models used in this tournament
    openai_models = set()
    mistral_models = set()
    
    for model_key in tournament_data["model_stats"].keys():
        provider, model = model_key.split('_', 1)
        if provider == "openai":
            openai_models.add(model)
        elif provider == "mistral":
            mistral_models.add(model)
    
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
        # Default naming
        folder_name = f"{datetime_str}_{num_games}games_{number_of_players}players_{model_counts}"
        
        # Add suffix if specified
        if folder_config.get("folder_suffix"):
            folder_name += folder_config["folder_suffix"]
    
    filename_base = f"{num_games}games_{number_of_players}players_{timestamp}"
    
    # Create the organized results directory structure
    base_results_dir = "/Users/nikitadmitrieff/Desktop/Projects/coding/L/Mister white AI/results"
    results_dir = os.path.join(base_results_dir, folder_name)
    os.makedirs(results_dir, exist_ok=True)
    
    # Create three CSV files: games summary, detailed player data, and messages
    
    # 1. Games Summary CSV
    games_csv_path = os.path.join(results_dir, f"{filename_base}_games.csv")
    with open(games_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'game_id', 'timestamp', 'secret_word', 'winner_side', 
            'mister_white_player', 'mister_white_provider', 'mister_white_model',
            'eliminated_player', 'eliminated_provider', 'eliminated_model',
            'total_votes_cast', 'vote_counts_json'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in tournament_data["results"]:
            writer.writerow({
                'game_id': result.game_id,
                'timestamp': result.timestamp,
                'secret_word': result.secret_word,
                'winner_side': result.winner_side,
                'mister_white_player': result.mister_white_player,
                'mister_white_provider': result.mister_white_model[0],
                'mister_white_model': result.mister_white_model[1],
                'eliminated_player': result.eliminated_player,
                'eliminated_provider': result.eliminated_model[0],
                'eliminated_model': result.eliminated_model[1],
                'total_votes_cast': sum(result.vote_counts.values()),
                'vote_counts_json': str(result.vote_counts)
            })
    
    # 2. Detailed Player Data CSV
    players_csv_path = os.path.join(results_dir, f"{filename_base}_players.csv")
    with open(players_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'game_id', 'player_name', 'provider', 'model', 
            'is_mister_white', 'word', 'survived', 'votes_received',
            'won_game', 'secret_word', 'winner_side'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in tournament_data["results"]:
            for player in result.players:
                won_game = (
                    (player['is_mister_white'] and result.winner_side == 'mister_white') or
                    (not player['is_mister_white'] and result.winner_side == 'citizens')
                )
                writer.writerow({
                    'game_id': result.game_id,
                    'player_name': player['name'],
                    'provider': player['provider'],
                    'model': player['model'],
                    'is_mister_white': player['is_mister_white'],
                    'word': player['word'],
                    'survived': player['survived'],
                    'votes_received': player['votes_received'],
                    'won_game': won_game,
                    'secret_word': result.secret_word,
                    'winner_side': result.winner_side
                })
    
    # 3. Messages CSV
    messages_csv_path = os.path.join(results_dir, f"{filename_base}_messages.csv")
    with open(messages_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'game_id', 'player_name', 'message_type', 'phase', 'round', 
            'content', 'secret_word', 'is_mister_white'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in tournament_data["results"]:
            # Create a lookup for player info
            player_lookup = {p['name']: p for p in result.players}
            
            for message in result.messages:
                player_info = player_lookup.get(message['player'], {})
                writer.writerow({
                    'game_id': result.game_id,
                    'player_name': message['player'],
                    'message_type': message['type'],
                    'phase': message['phase'],
                    'round': message['round'],
                    'content': message['content'],
                    'secret_word': result.secret_word,
                    'is_mister_white': player_info.get('is_mister_white', False)
                })
    
    # 4. Model Statistics CSV
    stats_csv_path = os.path.join(results_dir, f"{filename_base}_model_stats.csv")
    with open(stats_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'provider', 'model', 'games_played', 'total_wins', 'win_rate',
            'games_as_mister_white', 'wins_as_mister_white', 'mister_white_win_rate',
            'games_as_citizen', 'wins_as_citizen', 'citizen_win_rate',
            'eliminated_count', 'survival_rate', 'avg_votes_received'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for model_key, stats in tournament_data["model_stats"].items():
            provider, model = model_key.split('_', 1)
            writer.writerow({
                'provider': provider,
                'model': model,
                'games_played': stats['games_played'],
                'total_wins': stats['total_wins'],
                'win_rate': stats['win_rate'],
                'games_as_mister_white': stats['games_as_mister_white'],
                'wins_as_mister_white': stats['wins_as_mister_white'],
                'mister_white_win_rate': stats['mister_white_win_rate'],
                'games_as_citizen': stats['games_as_citizen'],
                'wins_as_citizen': stats['wins_as_citizen'],
                'citizen_win_rate': stats['citizen_win_rate'],
                'eliminated_count': stats['eliminated_count'],
                'survival_rate': stats['survival_rate'],
                'avg_votes_received': stats['avg_votes_received']
            })
    
    print(f"\n📊 CSV files saved in organized folder: {folder_name}")
    print(f"  • Games: {os.path.basename(games_csv_path)}")
    print(f"  • Players: {os.path.basename(players_csv_path)}")
    print(f"  • Messages: {os.path.basename(messages_csv_path)}")
    print(f"  • Model Stats: {os.path.basename(stats_csv_path)}")
    print(f"  • Full path: {results_dir}")
    
    return folder_name


def print_tournament_results(tournament_data: Dict[str, any]) -> None:
    """Print detailed tournament results and rankings."""
    
    model_stats = tournament_data["model_stats"]
    summary = tournament_data["summary"]
    
    print("\n" + "="*80)
    print("🏆 TOURNAMENT RESULTS")
    print("="*80)
    
    print(f"\nGames Played: {summary['total_games']}")
    print(f"Citizens Wins: {summary['citizens_wins']} ({summary['citizens_wins']/summary['total_games']*100:.1f}%)")
    print(f"Mister White Wins: {summary['mister_white_wins']} ({summary['mister_white_wins']/summary['total_games']*100:.1f}%)")
    
    # Sort models by overall win rate
    sorted_models = sorted(model_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)
    
    print("\n" + "🥇 MODEL RANKINGS (by overall win rate)".center(80))
    print("-" * 80)
    print(f"{'Rank':<4} {'Model':<25} {'Win Rate':<10} {'Games':<6} {'MW Rate':<8} {'Cit Rate':<9} {'Survival':<9}")
    print("-" * 80)
    
    for rank, (model_key, stats) in enumerate(sorted_models, 1):
        provider, model = model_key.split('_', 1)
        model_display = f"{provider}/{model}"
        if len(model_display) > 24:
            model_display = model_display[:21] + "..."
        
        print(f"{rank:<4} {model_display:<25} "
              f"{stats['win_rate']:.1%}      "
              f"{stats['games_played']:<6} "
              f"{stats['mister_white_win_rate']:.1%}     "
              f"{stats['citizen_win_rate']:.1%}      "
              f"{stats['survival_rate']:.1%}")
    
    print("\n" + "📊 DETAILED STATISTICS".center(80))
    print("-" * 80)
    
    for model_key, stats in sorted_models:
        provider, model = model_key.split('_', 1)
        print(f"\n{provider}/{model}:")
        print(f"  • Total Games: {stats['games_played']}")
        print(f"  • Overall Wins: {stats['total_wins']} ({stats['win_rate']:.1%})")
        print(f"  • As Mister White: {stats['wins_as_mister_white']}/{stats['games_as_mister_white']} ({stats['mister_white_win_rate']:.1%})")
        print(f"  • As Citizen: {stats['wins_as_citizen']}/{stats['games_as_citizen']} ({stats['citizen_win_rate']:.1%})")
        print(f"  • Times Eliminated: {stats['eliminated_count']} (Survival: {stats['survival_rate']:.1%})")
        print(f"  • Avg Votes Received: {stats['avg_votes_received']:.1f}")
