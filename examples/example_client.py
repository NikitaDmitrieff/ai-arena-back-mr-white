"""
Example client for the Mister White Game API.

This demonstrates how to:
1. Create a game
2. Connect to WebSocket for real-time updates
3. Get game status
"""

import asyncio
import json

import httpx
import websockets


API_BASE_URL = "http://localhost:8001/api/v1"
WS_BASE_URL = "ws://localhost:8001/api/v1"


async def create_game(models: list) -> str:
    """Create a new game and return the game ID."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/games",
            json={
                "models": models,
                "verbose": False,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        game_data = response.json()
        return game_data["game_id"]


async def get_game_status(game_id: str) -> dict:
    """Get current game status."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/games/{game_id}")
        response.raise_for_status()
        return response.json()


async def watch_game(game_id: str):
    """Watch a game in real-time via WebSocket."""
    uri = f"{WS_BASE_URL}/games/{game_id}/ws"

    async with websockets.connect(uri) as websocket:
        print(f"🔌 Connected to game {game_id}")
        print("📡 Listening for events...\n")

        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)

                event_type = event.get("event_type")
                data = event.get("data", {})

                if event_type == "connected":
                    print(f"✅ Connected - Status: {data.get('status')}")
                    print(f"   Phase: {data.get('phase')}\n")

                elif event_type == "phase_change":
                    print(f"📍 PHASE CHANGE: {data.get('phase')}")
                    print(f"   {data.get('message')}\n")

                elif event_type == "message":
                    msg_type = data.get("type")
                    player = data.get("player")
                    content = data.get("content")

                    emoji = {
                        "clue": "💡",
                        "discussion": "💬",
                        "vote": "🗳️",
                    }.get(msg_type, "📝")

                    print(f"{emoji} {msg_type.upper()}: {player}")
                    print(f"   {content}\n")

                elif event_type == "discussion_round":
                    print(f"🔄 Discussion Round {data.get('round')}\n")

                elif event_type == "game_complete":
                    print("=" * 60)
                    print("🎮 GAME COMPLETE!")
                    print("=" * 60)
                    print(f"🏆 Winner: {data.get('winner_side')}")
                    print(f"🔑 Secret word: {data.get('secret_word')}")
                    print(f"🎭 Mister White: {data.get('mister_white_player')}")
                    print(f"❌ Eliminated: {data.get('eliminated_player')}")
                    print(f"📊 Vote counts: {data.get('vote_counts')}")
                    print("=" * 60)
                    break

                elif event_type == "error":
                    print(f"❌ ERROR: {data.get('message')}")
                    break

            except websockets.exceptions.ConnectionClosed:
                print("🔌 Connection closed")
                break


async def list_games():
    """List all games."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/games")
        response.raise_for_status()
        return response.json()


async def main():
    """Main example flow."""
    print("🎮 Mister White Game API Client Example\n")

    # Define models for the game
    models = [
        {"provider": "mistral", "model": "mistral-small-latest"},
        {"provider": "mistral", "model": "mistral-medium-latest"},
        {"provider": "mistral", "model": "mistral-large-latest"},
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"provider": "openai", "model": "gpt-4o"},
    ]

    print("🚀 Creating new game...")
    print(f"   Models: {len(models)} players")
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model['provider']}/{model['model']}")
    print()

    # Create game
    game_id = await create_game(models)
    print(f"✅ Game created: {game_id}\n")

    # Watch game in real-time
    print("👀 Watching game in real-time...\n")
    await watch_game(game_id)

    # Get final status
    print("\n📊 Fetching final game status...")
    final_status = await get_game_status(game_id)
    print(f"Status: {final_status['status']}")
    print(f"Total messages: {len(final_status.get('messages', []))}")
    print(f"Total players: {len(final_status.get('players', []))}")


if __name__ == "__main__":
    asyncio.run(main())

