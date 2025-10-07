"""
Game state manager for concurrent game execution.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from api.models import GamePhase, GameStatus, PlayerInfo
from api.websocket_manager import ws_manager
from src.core.game import MisterWhiteGame, play_single_game
from src.core.models import GameResult

logger = logging.getLogger(__name__)


class GameState:
    """Represents the state of a single game."""

    def __init__(
        self,
        game_id: str,
        models: List[Tuple[str, str]],
        verbose: bool = False,
        secret_word: Optional[str] = None,
    ):
        self.game_id = game_id
        self.models = models
        self.verbose = verbose
        self.secret_word = secret_word
        self.status = GameStatus.PENDING
        self.phase = GamePhase.SETUP
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.result: Optional[GameResult] = None
        self.error: Optional[str] = None
        self.messages = []
        self.players = []

    def update_status(self, status: GameStatus) -> None:
        """Update game status and timestamp."""
        self.status = status
        self.updated_at = datetime.now()

    def update_phase(self, phase: GamePhase) -> None:
        """Update game phase and timestamp."""
        self.phase = phase
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert game state to dictionary for API response."""
        return {
            "game_id": self.game_id,
            "status": self.status.value,
            "phase": self.phase.value if self.phase else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "models": [
                {"provider": p, "model": m} for p, m in self.models
            ],
            "players": self.players,
            "messages": self.messages,
            "winner_side": self.result.winner_side if self.result else None,
            "eliminated_player": self.result.eliminated_player if self.result else None,
            "mister_white_player": (
                self.result.mister_white_player if self.result else None
            ),
            "secret_word": self.result.secret_word if self.result else None,
            "vote_counts": self.result.vote_counts if self.result else None,
            "error": self.error,
        }


class GameManager:
    """Manages all active and completed games."""

    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self._lock = asyncio.Lock()

    async def create_game(
        self,
        models: List[Tuple[str, str]],
        verbose: bool = False,
        secret_word: Optional[str] = None,
    ) -> str:
        """Create a new game and return its ID."""
        game_id = str(uuid.uuid4())
        async with self._lock:
            game_state = GameState(
                game_id=game_id,
                models=models,
                verbose=verbose,
                secret_word=secret_word,
            )
            self.games[game_id] = game_state
        logger.info(f"Created game {game_id} with {len(models)} players")
        return game_id

    async def get_game(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID."""
        return self.games.get(game_id)

    async def list_games(self) -> List[GameState]:
        """List all games."""
        return list(self.games.values())

    async def run_game(self, game_id: str) -> None:
        """Execute a game asynchronously with real-time updates."""
        game_state = await self.get_game(game_id)
        if not game_state:
            logger.error(f"Game {game_id} not found")
            return

        try:
            game_state.update_status(GameStatus.RUNNING)
            await ws_manager.send_event(
                game_id,
                "status_change",
                {"status": "running", "message": "Game started"},
            )

            # Run game in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_game_with_events,
                game_id,
                game_state,
            )

            # Store result
            game_state.result = result
            game_state.update_status(GameStatus.COMPLETED)

            # Build final player info
            game_state.players = [
                {
                    "name": p["name"],
                    "provider": p["provider"],
                    "model": p["model"],
                    "is_mister_white": p["is_mister_white"],
                    "word": p["word"],
                    "survived": p["survived"],
                    "votes_received": p["votes_received"],
                }
                for p in result.players
            ]

            # Send completion event
            await ws_manager.send_event(
                game_id,
                "game_complete",
                {
                    "winner_side": result.winner_side,
                    "secret_word": result.secret_word,
                    "mister_white_player": result.mister_white_player,
                    "eliminated_player": result.eliminated_player,
                    "vote_counts": result.vote_counts,
                },
            )

            logger.info(
                f"Game {game_id} completed. Winner: {result.winner_side}"
            )

        except Exception as e:
            logger.exception(f"Error running game {game_id}: {str(e)}")
            game_state.error = str(e)
            game_state.update_status(GameStatus.FAILED)
            await ws_manager.send_event(
                game_id, "error", {"message": str(e)}
            )

    def _execute_game_with_events(
        self, game_id: str, game_state: GameState
    ) -> GameResult:
        """Execute game synchronously and send events via WebSocket (runs in executor)."""
        import random

        from src.config import constants

        # Use constants for names and words
        names = constants.NAMES
        words = constants.SECRET_WORD

        # Select secret word
        if game_state.secret_word:
            selected_word = game_state.secret_word
        else:
            selected_word = random.choice(words)

        # Initialize game
        game = MisterWhiteGame()
        number_of_players = len(game_state.models)

        for i in range(number_of_players):
            name = names[i]
            provider, model = game_state.models[i]
            game.add_player(name=name, provider=provider, model=model)

        game.set_secret_word(selected_word)

        # Assign roles (using game_id hash for distribution)
        mister_white_index = hash(game_id) % number_of_players
        game.start(mister_white_index=mister_white_index)

        # Send phase change event
        asyncio.run(
            ws_manager.send_event(
                game_id,
                "phase_change",
                {
                    "phase": "setup",
                    "message": f"Game initialized with {number_of_players} players",
                },
            )
        )

        # Build initial player info (without revealing roles)
        game_state.players = [
            {
                "name": p.name,
                "provider": game_state.models[i][0],
                "model": game_state.models[i][1],
                "is_mister_white": False,  # Hide until game ends
                "word": None,  # Hide until game ends
                "survived": None,
                "votes_received": None,
            }
            for i, p in enumerate(game.players)
        ]

        # CLUE PHASE
        asyncio.run(
            ws_manager.send_event(
                game_id,
                "phase_change",
                {"phase": "clue", "message": "Players giving clues"},
            )
        )
        game_state.update_phase(GamePhase.CLUE)

        # Regular players give clues first
        from src.prompts import prompts

        for player in game.players:
            if not player.is_mister_white:
                system_prompt = prompts.REGULAR_PLAYER_CLUE_SYSTEM.format(
                    word=player.word
                )
                user_prompt = prompts.REGULAR_PLAYER_CLUE_USER.format(
                    word=player.word
                )
                clue = player.invoke(user_prompt, system_prompt)

                message = {
                    "player": player.name,
                    "type": "clue",
                    "content": clue,
                    "round": 0,
                    "phase": "clue",
                }
                game.messages.append(message)
                game_state.messages.append(message)

                # Send message event
                asyncio.run(
                    ws_manager.send_event(
                        game_id, "message", message
                    )
                )

        # Mister White gives clue after seeing others
        mister_white = next(p for p in game.players if p.is_mister_white)
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
        clue = mister_white.invoke(user_prompt, system_prompt)

        message = {
            "player": mister_white.name,
            "type": "clue",
            "content": clue,
            "round": 0,
            "phase": "clue",
        }
        game.messages.append(message)
        game_state.messages.append(message)
        asyncio.run(ws_manager.send_event(game_id, "message", message))

        # DISCUSSION PHASE
        asyncio.run(
            ws_manager.send_event(
                game_id,
                "phase_change",
                {"phase": "discussion", "message": "Discussion rounds starting"},
            )
        )
        game_state.update_phase(GamePhase.DISCUSSION)

        for round_num in range(1, 3):
            asyncio.run(
                ws_manager.send_event(
                    game_id,
                    "discussion_round",
                    {"round": round_num, "message": f"Discussion round {round_num}"},
                )
            )

            for player in game.players:
                context = "\n".join(
                    [
                        f"{msg['player']}: {msg['content']}"
                        for msg in game.messages
                        if msg["type"] in ["clue", "discussion"]
                    ]
                )

                system_prompt = prompts.DISCUSSION_SYSTEM.format(
                    player_name=player.name
                )
                if player.is_mister_white:
                    user_prompt = prompts.MISTER_WHITE_DISCUSSION_USER.format(
                        context=context
                    )
                else:
                    user_prompt = prompts.REGULAR_PLAYER_DISCUSSION_USER.format(
                        context=context, word=player.word
                    )

                response = player.invoke(user_prompt, system_prompt)
                message = {
                    "player": player.name,
                    "type": "discussion",
                    "content": response,
                    "round": round_num,
                    "phase": "discussion",
                }
                game.messages.append(message)
                game_state.messages.append(message)
                asyncio.run(
                    ws_manager.send_event(game_id, "message", message)
                )

        # VOTING PHASE
        asyncio.run(
            ws_manager.send_event(
                game_id,
                "phase_change",
                {"phase": "voting", "message": "Voting phase starting"},
            )
        )
        game_state.update_phase(GamePhase.VOTING)

        votes = {}
        all_messages = [
            f"{msg['player']}: {msg['content']}" for msg in game.messages
        ]
        shuffled_messages = all_messages.copy()
        random.shuffle(shuffled_messages)
        shuffled_context = "\n".join(shuffled_messages)

        for player in game.players:
            system_prompt = prompts.VOTING_SYSTEM.format(
                player_name=player.name,
                players=f"{[p.name for p in game.players]}",
            )

            if player.is_mister_white:
                user_prompt = prompts.MISTER_WHITE_VOTING_USER.format(
                    context=shuffled_context
                )
            else:
                user_prompt = prompts.CITIZEN_VOTING_USER.format(
                    context=shuffled_context, word=player.word
                )

            vote = player.invoke(user_prompt, system_prompt).strip()
            message = {
                "player": player.name,
                "type": "vote",
                "content": vote,
                "round": 1,
                "phase": "voting",
            }
            game.messages.append(message)
            game_state.messages.append(message)
            votes[player.name] = vote
            asyncio.run(
                ws_manager.send_event(game_id, "message", message)
            )

        # Count votes
        vote_counts = {}
        for voter, voted_for in votes.items():
            vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1

        # Determine winner
        eliminated = (
            max(vote_counts.items(), key=lambda x: x[1])[0]
            if vote_counts
            else ""
        )
        eliminated_player = None
        for p in game.players:
            if p.name.lower() == eliminated.lower():
                eliminated_player = p
                break

        mister_white_player = next(
            p for p in game.players if p.is_mister_white
        )
        winner_side = (
            "citizens"
            if eliminated_player and eliminated_player.is_mister_white
            else "mister_white"
        )

        # Build player models map
        player_models = {}
        for i, player in enumerate(game.players):
            provider, model = game_state.models[i]
            player_models[player.name] = (provider, model)

        # Create players info
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

        # Create result
        result = GameResult(
            game_id=hash(game_id),  # Use hash for integer game_id
            timestamp=datetime.now().isoformat(),
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

        return result


# Global game manager instance
game_manager = GameManager()

