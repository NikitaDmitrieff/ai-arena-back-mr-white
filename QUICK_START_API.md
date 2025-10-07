# 🚀 Quick Start: Mister White API

## Start the API Server

```bash
# Option 1: Use the convenience script
./run_api.sh

# Option 2: Direct uvicorn command
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: **http://localhost:8001**

## 📚 Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

These provide interactive API exploration where you can:
- See all endpoints
- Test API calls directly in browser
- View request/response schemas

## 🎮 Create Your First Game

### Option 1: Using cURL

```bash
curl -X POST http://localhost:8001/api/v1/games \
  -H "Content-Type: application/json" \
  -d '{
    "models": [
      {"provider": "mistral", "model": "mistral-small-latest"},
      {"provider": "openai", "model": "gpt-4o-mini"},
      {"provider": "mistral", "model": "mistral-large-latest"}
    ],
    "verbose": false
  }'
```

### Option 2: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/games",
    json={
        "models": [
            {"provider": "mistral", "model": "mistral-small-latest"},
            {"provider": "openai", "model": "gpt-4o-mini"},
            {"provider": "mistral", "model": "mistral-large-latest"},
        ]
    }
)

game = response.json()
print(f"Game created: {game['game_id']}")
```

### Option 3: Run Example Client

```bash
python3 examples/example_client.py
```

This runs a complete example with WebSocket streaming!

## 🔌 Watch Game in Real-Time

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def watch_game(game_id):
    uri = f"ws://localhost:8001/api/v1/games/{game_id}/ws"
    
    async with websockets.connect(uri) as ws:
        print(f"Connected to game {game_id}")
        
        while True:
            message = await ws.recv()
            event = json.loads(message)
            
            print(f"\n[{event['event_type']}]")
            print(json.dumps(event['data'], indent=2))
            
            if event['event_type'] == 'game_complete':
                break

# Use the game_id from game creation
asyncio.run(watch_game("your-game-id-here"))
```

## 📊 Check Game Status

### Get Specific Game

```bash
curl http://localhost:8001/api/v1/games/{game_id}
```

### List All Games

```bash
curl http://localhost:8001/api/v1/games
```

## 🎯 Common Use Cases

### 1. Quick Test (Polling)

```python
import requests
import time

# Create game
resp = requests.post("http://localhost:8001/api/v1/games", json={
    "models": [
        {"provider": "mistral", "model": "mistral-small-latest"},
        {"provider": "mistral", "model": "mistral-medium-latest"},
        {"provider": "mistral", "model": "mistral-large-latest"},
    ]
})
game_id = resp.json()["game_id"]

# Poll until complete
while True:
    status = requests.get(f"http://localhost:8001/api/v1/games/{game_id}").json()
    if status["status"] == "completed":
        print(f"Winner: {status['winner_side']}")
        print(f"Secret word: {status['secret_word']}")
        break
    print(f"Status: {status['status']}, Phase: {status.get('phase')}")
    time.sleep(2)
```

### 2. Watch Multiple Games

```python
import asyncio
import httpx
import websockets

async def run_and_watch_multiple_games():
    # Create 3 games
    async with httpx.AsyncClient() as client:
        game_ids = []
        for i in range(3):
            resp = await client.post("http://localhost:8001/api/v1/games", json={
                "models": [
                    {"provider": "mistral", "model": "mistral-small-latest"},
                    {"provider": "openai", "model": "gpt-4o-mini"},
                    {"provider": "mistral", "model": "mistral-large-latest"},
                ]
            })
            game_ids.append(resp.json()["game_id"])
    
    # Watch all games concurrently
    async def watch(game_id):
        async with websockets.connect(f"ws://localhost:8001/api/v1/games/{game_id}/ws") as ws:
            while True:
                event = json.loads(await ws.recv())
                if event['event_type'] == 'game_complete':
                    return event['data']
    
    results = await asyncio.gather(*[watch(gid) for gid in game_ids])
    return results

results = asyncio.run(run_and_watch_multiple_games())
print(f"All {len(results)} games completed!")
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### Available Models

**OpenAI:**
- `gpt-4o-mini` (recommended, fast)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

**Mistral:**
- `mistral-small-latest` (recommended)
- `mistral-medium-latest`
- `mistral-large-latest`
- `mistral-tiny`
- `open-mistral-7b`
- `open-mixtral-8x7b`
- `open-mixtral-8x22b`

## 📝 Game Event Types

When watching via WebSocket, you'll receive these events:

| Event Type | Description | When |
|------------|-------------|------|
| `connected` | Connection established | On connect |
| `phase_change` | Game phase transition | Setup → Clue → Discussion → Voting |
| `message` | Player action | Clue, discussion, vote |
| `discussion_round` | Round indicator | Start of each discussion round |
| `game_complete` | Game finished | After voting |
| `error` | Error occurred | On game failure |

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
uvicorn api.main:app --port 9000
```

### WebSocket connection fails

```bash
# Make sure you're using ws:// (not wss://) for local
ws://localhost:8001/api/v1/games/{game_id}/ws
```

### Game creation fails

```bash
# Check API keys are set
cat .env

# Check server logs for detailed error
# They will show LLM API errors
```

### Game takes too long

- Normal: Games take 30-60 seconds (LLM API calls)
- Each player makes multiple LLM calls
- Watch via WebSocket to see progress in real-time

## 📦 Example Projects

Check the `examples/` directory:

1. **example_client.py** - Full-featured async client with WebSocket
2. **simple_client.py** - Simple synchronous client with polling

Run them:
```bash
python3 examples/example_client.py
python3 examples/simple_client.py
```

## 🎓 Next Steps

1. ✅ Start the API server
2. ✅ Try the example clients
3. ✅ Explore the interactive docs at `/docs`
4. ✅ Build your own client integration
5. 📚 Read full documentation:
   - [API_README.md](API_README.md) - Complete API reference
   - [API_ARCHITECTURE.md](API_ARCHITECTURE.md) - Technical details

## 💡 Tips

- Use WebSocket for best user experience (real-time updates)
- Run multiple games concurrently (they don't block each other)
- Check game status before connecting WebSocket (game must exist)
- Games are kept in memory until server restarts
- Use 3-5 players for faster games (fewer LLM calls)

## 🎉 You're Ready!

Start building your integration with the Mister White Game API!

Need help? Check the full documentation or explore the interactive API docs.

