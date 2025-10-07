"""
API routes for Mister White game management.
"""

import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect

from api.game_manager import game_manager
from api.models import (
    CreateGameRequest,
    GameListResponse,
    GameResponse,
    HealthResponse,
)
from api.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@router.post("/games", response_model=GameResponse, status_code=201)
async def create_game(
    request: CreateGameRequest, background_tasks: BackgroundTasks
):
    """
    Create and start a new game.
    
    The game will run asynchronously in the background.
    Use WebSocket connection to receive real-time updates.
    """
    try:
        # Convert models to tuples
        models = [(m.provider, m.model) for m in request.models]

        # Create game
        game_id = await game_manager.create_game(
            models=models,
            verbose=request.verbose,
            secret_word=request.secret_word,
        )

        # Start game in background
        background_tasks.add_task(game_manager.run_game, game_id)

        # Get initial game state
        game_state = await game_manager.get_game(game_id)
        return GameResponse(**game_state.to_dict())

    except Exception as e:
        logger.exception(f"Error creating game: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """Get game status and details."""
    game_state = await game_manager.get_game(game_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameResponse(**game_state.to_dict())


@router.get("/games", response_model=GameListResponse)
async def list_games():
    """List all games."""
    games = await game_manager.list_games()
    game_responses = [GameResponse(**g.to_dict()) for g in games]
    return GameListResponse(games=game_responses, total=len(game_responses))


@router.websocket("/games/{game_id}/ws")
async def game_websocket(websocket: WebSocket, game_id: str):
    """
    WebSocket endpoint for real-time game updates.
    
    Events sent:
    - phase_change: Game phase transitions
    - message: Player messages (clues, discussion, votes)
    - game_complete: Final game results
    - error: Error messages
    """
    # Check if game exists
    game_state = await game_manager.get_game(game_id)
    if not game_state:
        await websocket.close(code=1008, reason="Game not found")
        return

    await ws_manager.connect(game_id, websocket)

    try:
        # Send initial status
        await websocket.send_json(
            {
                "event_type": "connected",
                "data": {
                    "game_id": game_id,
                    "status": game_state.status.value,
                    "phase": game_state.phase.value if game_state.phase else None,
                },
            }
        )

        # Keep connection alive and listen for client messages (if any)
        while True:
            # Wait for any messages from client (just to keep connection alive)
            await websocket.receive_text()

    except WebSocketDisconnect:
        ws_manager.disconnect(game_id, websocket)
        logger.info(f"WebSocket disconnected for game {game_id}")
    except Exception as e:
        logger.error(f"WebSocket error for game {game_id}: {str(e)}")
        ws_manager.disconnect(game_id, websocket)

