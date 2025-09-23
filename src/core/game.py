"""
Core game mechanics for Mister White.
Contains the game engine and single game execution logic.
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.config import constants
from src.core.agent import Player
from src.core.models import GameResult
from src.prompts import prompts


class MisterWhiteGame:
    """Core Mister White game engine.

    This class provides the minimal building blocks:
    - add players
    - set the secret word
    - assign roles (one Mister White, others get the word)
    - expose a per-player view of their role/word

    Game rounds, clues, voting, and scoring are handled by play_single_game.
    """

    def __init__(self) -> None:
        self.players: List[Player] = []
        self.secret_word: Optional[str] = None
        self._started: bool = False
        self._mister_white_index: Optional[int] = None
        self.messages: List[Dict[str, str]] = []

    # Setup API
    def add_player(
        self, name: str, provider: str = "openai", model: str = "gpt-4o-mini"
    ) -> Player:
        player = Player(
            name=name.strip(),
            description=f"AI player named {name.strip()}",
            provider=provider,
            model=model,
        )
        self.players.append(player)
        return self.players[-1]

    def set_secret_word(self, word: str) -> None:
        word = (word or "").strip()
        self.secret_word = word

    # Lifecycle
    def start(
        self,
        *,
        random_seed: Optional[int] = None,
        mister_white_index: Optional[int] = None,
    ) -> None:
        self._assign_roles(
            random_seed=random_seed, mister_white_index=mister_white_index
        )
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
    def _assign_roles(
        self,
        *,
        random_seed: Optional[int] = None,
        mister_white_index: Optional[int] = None,
    ) -> None:
        if random_seed is not None:
            random.seed(random_seed)

        # Use provided index for even distribution, or random as fallback
        if mister_white_index is not None:
            self._mister_white_index = mister_white_index
        else:
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


def play_single_game(
    game_id: int,
    names: List[str] = None,
    words: List[str] = None,
    models: List[Tuple[str, str]] = None,
    verbose: bool = True,
    random_seed: Optional[int] = None,
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

    # Number of players is determined by number of models (one player per model)
    number_of_players = len(models)

    # Initialize and start the game
    if random_seed is not None:
        random.seed(random_seed)

    game = MisterWhiteGame()
    for i in range(number_of_players):
        name = names[i]
        # Each model gets exactly one player
        provider, model = models[i]
        game.add_player(name=name, provider=provider, model=model)

    selected_word = random.choice(words)
    game.set_secret_word(selected_word)

    # Distribute Mister White role evenly across models instead of randomly
    # Use game_id to cycle through models for fair distribution
    mister_white_index = (game_id - 1) % number_of_players

    # Ensure Mister White is always named Emily
    if "Emily" not in [p.name for p in game.players]:
        # If Emily isn't already assigned, use a different name for Mister White
        game.players[mister_white_index].name = "Emily"
    else:
        # If Emily is already assigned, find Emily and make her Mister White
        emily_index = next(i for i, p in enumerate(game.players) if p.name == "Emily")
        if emily_index != mister_white_index:
            # Swap names so Emily becomes Mister White
            original_mw_name = game.players[mister_white_index].name
            game.players[mister_white_index].name = "Emily"
            game.players[emily_index].name = original_mw_name

    game.start(random_seed=random_seed, mister_white_index=mister_white_index)

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
            game.messages.append(
                {
                    "player": player.name,
                    "type": "clue",
                    "content": clue,
                    "round": 0,
                    "phase": "clue",
                }
            )
            if verbose:
                print(f"{player.name}: {clue}")

    # Then, let Mister White give their clue after seeing others' clues
    mister_white = next(p for p in game.players if p.is_mister_white)
    if game.messages:  # If there are previous clues
        previous_clues = "\n".join(
            [
                f"{msg['player']}: {msg['content']}"
                for msg in game.messages
                if msg["type"] == "clue"
            ]
        )
        system_prompt = prompts.MISTER_WHITE_CLUE_WITH_CONTEXT_SYSTEM
        user_prompt = prompts.MISTER_WHITE_CLUE_WITH_CONTEXT_USER.format(
            previous_clues=previous_clues
        )
    else:
        raise ValueError("No previous clues found")

    clue = mister_white.invoke(user_prompt, system_prompt)
    game.messages.append(
        {
            "player": mister_white.name,
            "type": "clue",
            "content": clue,
            "round": 0,
            "phase": "clue",
        }
    )
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
            context = "\n".join(
                [
                    f"{msg['player']}: {msg['content']}"
                    for msg in game.messages
                    if msg["type"] in ["clue", "discussion"]
                ]
            )

            system_prompt = prompts.DISCUSSION_SYSTEM.format(player_name=player.name)
            if player.is_mister_white:
                user_prompt = prompts.MISTER_WHITE_DISCUSSION_USER.format(
                    context=context
                )
            else:
                user_prompt = prompts.REGULAR_PLAYER_DISCUSSION_USER.format(
                    context=context, word=player.word
                )

            response = player.invoke(user_prompt, system_prompt)
            game.messages.append(
                {
                    "player": player.name,
                    "type": "discussion",
                    "content": response,
                    "round": round_num,
                    "phase": "discussion",
                }
            )
            if verbose:
                print(f"{player.name}: {response}")

    # Voting phase
    if verbose:
        print("\n--- Voting Phase ---")
    votes = {}

    # Create randomized context to remove order-based voting cues
    all_messages = [f"{msg['player']}: {msg['content']}" for msg in game.messages]
    shuffled_messages = all_messages.copy()
    random.shuffle(shuffled_messages)
    shuffled_context = "\n".join(shuffled_messages)

    for player in game.players:
        system_prompt = prompts.VOTING_SYSTEM.format(
            player_name=player.name, players=f"{[p.name for p in game.players]}"
        )

        # Use role-specific voting prompts
        if player.is_mister_white:
            user_prompt = prompts.MISTER_WHITE_VOTING_USER.format(
                context=shuffled_context
            )
        else:
            user_prompt = prompts.CITIZEN_VOTING_USER.format(
                context=shuffled_context, word=player.word
            )

        vote = player.invoke(user_prompt, system_prompt).strip()
        game.messages.append(
            {
                "player": player.name,
                "type": "vote",
                "content": vote,
                "round": 1,
                "phase": "voting",
            }
        )
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
    winner_side = (
        "citizens"
        if eliminated_player and eliminated_player.is_mister_white
        else "mister_white"
    )

    if verbose:
        print("\n=== GAME RESULTS ===")
        print(f"Vote results: {vote_counts}")
        print(f"Eliminated: {eliminated}")

        if winner_side == "citizens":
            print("🎉 Citizens win! Mister White was caught!")
        else:
            print(
                f"💀 Mister White ({mister_white_player.name}) wins! An innocent was eliminated."
            )

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
        players_info.append(
            {
                "name": player.name,
                "provider": provider,
                "model": model,
                "is_mister_white": player.is_mister_white,
                "word": player.word,
                "survived": player.name != eliminated,
                "votes_received": vote_counts.get(player.name, 0),
            }
        )

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
        messages=game.messages,
    )
