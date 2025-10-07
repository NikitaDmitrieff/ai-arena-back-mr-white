"""
Pydantic models for FastAPI request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """LLM model configuration."""

    provider: str = Field(..., description="Provider name (openai, mistral)")
    model: str = Field(..., description="Model identifier")


class GameStatus(str, Enum):
    """Game status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GamePhase(str, Enum):
    """Game phase enumeration."""

    SETUP = "setup"
    CLUE = "clue"
    DISCUSSION = "discussion"
    VOTING = "voting"
    RESULTS = "results"


class CreateGameRequest(BaseModel):
    """Request to create a new game."""

    models: List[ModelConfig] = Field(
        ..., min_length=3, max_length=10, description="List of models to play (3-10)"
    )
    verbose: bool = Field(default=False, description="Enable verbose game logging")
    secret_word: Optional[str] = Field(
        default=None, description="Optional secret word (random if not provided)"
    )


class PlayerInfo(BaseModel):
    """Player information in a game."""

    name: str
    provider: str
    model: str
    is_mister_white: bool
    word: Optional[str] = None  # Hidden until game ends
    survived: Optional[bool] = None  # Only available after game ends
    votes_received: Optional[int] = None  # Only available after game ends


class GameMessage(BaseModel):
    """A message/event in the game."""

    player: str
    type: str  # "clue", "discussion", "vote"
    content: str
    round: int
    phase: str
    timestamp: datetime = Field(default_factory=datetime.now)


class GameEvent(BaseModel):
    """Real-time game event for WebSocket streaming."""

    event_type: str  # "phase_change", "message", "game_complete", "error"
    data: Dict
    timestamp: datetime = Field(default_factory=datetime.now)


class GameResponse(BaseModel):
    """Response containing game information."""

    game_id: str
    status: GameStatus
    phase: Optional[GamePhase] = None
    created_at: datetime
    updated_at: datetime
    models: List[ModelConfig]
    players: Optional[List[PlayerInfo]] = None
    messages: Optional[List[GameMessage]] = None
    winner_side: Optional[str] = None  # "citizens" or "mister_white"
    eliminated_player: Optional[str] = None
    mister_white_player: Optional[str] = None
    secret_word: Optional[str] = None  # Only revealed when game is complete
    vote_counts: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class GameListResponse(BaseModel):
    """Response containing list of games."""

    games: List[GameResponse]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)

