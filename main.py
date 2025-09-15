from __future__ import annotations

import random
from typing import List, Optional, Dict

import constants
import prompts
from agent import Player


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


def main() -> None:    # Collect players (very simple CLI)

    # Starting parameters
    number_of_players = 5
    names = constants.NAMES
    word = constants.SECRET_WORD
    models = constants.PROVIDERS_AND_MODELS

    # Initialize and start the game
    game = MisterWhiteGame()
    for i in range(number_of_players):
        name = names[i]
        # Cycle through available models for variety
        provider, model = models[i]
        game.add_player(name=name, provider=provider, model=model)
    game.set_secret_word(random.choice(word))
    game.start()

    for p in game.players:
        print(f"- {p.name}: {game.get_player_view(p.name)}")

    ### Record all the messages within game
    # 1. Query each agent for their word
    print("\n=== WORD PHASE ===")
    
    # First, let non-Mister White players give their clues
    for player in game.players:
        if not player.is_mister_white:
            system_prompt = prompts.REGULAR_PLAYER_CLUE_SYSTEM.format(word=player.word)
            user_prompt = prompts.REGULAR_PLAYER_CLUE_USER.format(word=player.word)
            
            clue = player.invoke(user_prompt, system_prompt)
            game.messages.append({"player": player.name, "type": "clue", "content": clue})
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
    game.messages.append({"player": mister_white.name, "type": "clue", "content": clue})
    print(f"{mister_white.name}: {clue}")

    # 2. Killing round
    print("\n=== KILLING ROUND ===")
    #    a. Each agent gets two chances to talk
    print("\n--- Discussion Phase (2 rounds) ---")
    for round_num in range(1, 3):
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
            game.messages.append({"player": player.name, "type": "discussion", "content": response})
            print(f"{player.name}: {response}")

    #    b. Each agent gets one chance to vote
    print("\n--- Voting Phase ---")
    votes = {}
    for player in game.players:
        # Build context of all messages
        context = "\n".join([f"{msg['player']}: {msg['content']}" for msg in game.messages])
        
        system_prompt = prompts.VOTING_SYSTEM.format(player_name=player.name)
        user_prompt = prompts.VOTING_USER.format(context=context)
        
        vote = player.invoke(user_prompt, system_prompt).strip()
        game.messages.append({"player": player.name, "type": "vote", "content": vote})
        votes[player.name] = vote
        print(f"{player.name} votes for: {vote}")

    # Count votes and determine result
    print("\n=== GAME RESULTS ===")
    vote_counts = {}
    for voter, voted_for in votes.items():
        vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1
    
    # Find player with most votes
    if vote_counts:
        eliminated = max(vote_counts.items(), key=lambda x: x[1])[0]
        eliminated_player = None
        for p in game.players:
            if p.name.lower() == eliminated.lower():
                eliminated_player = p
                break
        
        print(f"Vote results: {vote_counts}")
        print(f"Eliminated: {eliminated}")
        
        if eliminated_player and eliminated_player.is_mister_white:
            print("🎉 Citizens win! Mister White was caught!")
        else:
            mister_white = next(p for p in game.players if p.is_mister_white)
            print(f"💀 Mister White ({mister_white.name}) wins! An innocent was eliminated.")
    
    print(f"\nThe secret word was: {game.secret_word}")
    print(f"Mister White was: {next(p.name for p in game.players if p.is_mister_white)}")



if __name__ == "__main__":
    main()
