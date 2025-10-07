# Mister White AI Tournament

AI tournament system for the social deduction game "Mister White" using multiple LLM providers. Features a modular architecture for easy extension and comprehensive data analysis.

## 🚀 Two Ways to Use

### 1. REST API (New! 🎮)

Run games via FastAPI with real-time WebSocket updates:

```bash
# Start API server
./run_api.sh
# or
uvicorn api.main:app --reload --port 8001

# API available at http://localhost:8001
# Documentation at http://localhost:8001/docs
```

**Features:**
- ✅ RESTful API for game management
- 🔌 WebSocket support for real-time updates
- 🎮 Concurrent game support
- 📡 Perfect for integrating with other services

See [API_README.md](API_README.md) for detailed API documentation.

### 2. Command Line (Original)

Run tournaments directly from the command line:

1. **Set up API keys** in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   MISTRAL_API_KEY=your_key_here
   ```

2. **Configure simulation** in `simulation_config.json`:
   - Set tournament parameters (`num_games`)
   - Select enabled models (determines number of players)
   - Optionally set custom folder naming

3. **Run tournament**:
   ```bash
   python main.py
   ```

## Game Flow

- **Dynamic players**: Number of players = number of enabled models
- **Word Phase**: Players give clues, Mister White guesses blind after seeing others
- **Discussion Phase**: 2 rounds of suspicion discussion  
- **Voting Phase**: Eliminate suspected Mister White
- **Result**: Citizens win if Mister White eliminated, otherwise Mister White wins

## Configuration

### Complete Configuration (`simulation_config.json`)
```json
{
  "tournament_config": {
    "num_games": 10,
    "verbose": false,
    "show_progress": true
  },
  "folder_naming": {
    "custom_folder_name": "my_experiment",
    "use_custom_only": true
  },
  "enabled_models": [
    {"provider": "openai", "model": "gpt-4o-mini"},
    {"provider": "mistral", "model": "mistral-small-latest"},
    {"provider": "mistral", "model": "mistral-large-latest"}
  ]
}
```

### Tournament Parameters
- `num_games`: Number of games to run (epochs)
- `verbose`: Show detailed game output
- `show_progress`: Display progress during tournament
- Players per game automatically determined by number of enabled models

### Model Selection
Each enabled model becomes one player in every game. Mister White role is distributed evenly across models over multiple games for fair comparison.

### Fault Tolerance
The system includes robust error handling:
- **Partial Results Saved**: If any game fails (rate limits, network issues, etc.), all completed games are automatically saved
- **Graceful Failure**: Tournament stops gracefully with clear error reporting
- **No Data Loss**: Results from successful games are preserved even if later games fail
- **Clear Status**: File names and reports clearly indicate partial vs complete tournaments

## Output

Results saved in organized CSV files:
- `results/{date_time}_{params}/` (or `{params}_partial/` for failed tournaments)
  - `*_games.csv` - Game outcomes
  - `*_players.csv` - Player performance 
  - `*_messages.csv` - All conversations
  - `*_model_stats.csv` - Model statistics
  - `*_tournament_summary.csv` - Tournament metadata and status

## Architecture

The codebase uses a clean modular architecture:

### Core Game Engine
- `main.py` - Entry point and high-level orchestration
- `config.py` - Configuration loading and management  
- `game.py` - Core game mechanics and single game execution
- `tournament.py` - Multi-game tournament management
- `data_export.py` - CSV export and data persistence
- `results.py` - Console results display and analysis
- `models.py` - Data structures and type definitions
- `agent.py` - LLM integration and player implementation
- `prompts.py` - All game prompts and instructions
- `constants.py` - Static configuration and defaults

### FastAPI (New!)
- `api/main.py` - FastAPI application entry point
- `api/routes.py` - REST API endpoints
- `api/models.py` - Pydantic models for API validation
- `api/game_manager.py` - Concurrent game execution manager
- `api/websocket_manager.py` - Real-time event broadcasting
- `examples/` - Example client implementations

See `CODEBASE.md` for core architecture and `API_ARCHITECTURE.md` for API details.

## Requirements

- Python 3.13+
- OpenAI and/or Mistral API access
- Dependencies installed via `uv sync` or `pip install -e .`

## Documentation

- [README.md](README.md) - This file (overview and quick start)
- [CODEBASE.md](CODEBASE.md) - Core game engine architecture
- [API_README.md](API_README.md) - FastAPI usage and examples
- [API_ARCHITECTURE.md](API_ARCHITECTURE.md) - Detailed API architecture
- [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Frontend integration guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Docker deployment guide

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t mrwhite-backend .

# Run container
docker run -d \
  -p 8001:8001 \
  -e OPENAI_API_KEY=your_key \
  -e MISTRAL_API_KEY=your_key \
  --name mrwhite-backend \
  mrwhite-backend
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment with GitHub Actions.
