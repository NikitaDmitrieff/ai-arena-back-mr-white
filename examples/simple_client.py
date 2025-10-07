"""
Simple synchronous client example using requests.

This is a simpler alternative that doesn't use WebSocket,
just polls for game completion.
"""

import time

import requests


API_BASE_URL = "http://localhost:8001/api/v1"


def create_game(models: list) -> str:
    """Create a new game."""
    response = requests.post(
        f"{API_BASE_URL}/games",
        json={"models": models, "verbose": False},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["game_id"]


def get_game_status(game_id: str) -> dict:
    """Get game status."""
    response = requests.get(f"{API_BASE_URL}/games/{game_id}")
    response.raise_for_status()
    return response.json()


def wait_for_game(game_id: str, poll_interval: float = 2.0):
    """Poll game status until complete."""
    print(f"⏳ Waiting for game {game_id} to complete...")

    while True:
        status = get_game_status(game_id)

        if status["status"] == "completed":
            print("✅ Game completed!")
            return status
        elif status["status"] == "failed":
            print(f"❌ Game failed: {status.get('error')}")
            return status

        print(f"   Status: {status['status']}, Phase: {status.get('phase')}")
        time.sleep(poll_interval)


def main():
    """Simple example."""
    print("🎮 Simple Mister White Game Client\n")

    # Define models
    models = [
        {"provider": "mistral", "model": "mistral-small-latest"},
        {"provider": "mistral", "model": "mistral-medium-latest"},
        {"provider": "mistral", "model": "mistral-large-latest"},
    ]

    print(f"🚀 Creating game with {len(models)} players...")
    game_id = create_game(models)
    print(f"✅ Game created: {game_id}\n")

    # Wait for completion
    final_status = wait_for_game(game_id)

    # Print results
    print("\n" + "=" * 60)
    print("🎮 GAME RESULTS")
    print("=" * 60)
    print(f"Winner: {final_status.get('winner_side')}")
    print(f"Secret word: {final_status.get('secret_word')}")
    print(f"Mister White: {final_status.get('mister_white_player')}")
    print(f"Eliminated: {final_status.get('eliminated_player')}")
    print(f"Vote counts: {final_status.get('vote_counts')}")
    print("=" * 60)


if __name__ == "__main__":
    main()

