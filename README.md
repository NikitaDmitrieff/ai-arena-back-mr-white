# Mister White AI Tournament

AI tournament system for the social deduction game "Mister White" using multiple LLM providers. Features a modular architecture for easy extension and comprehensive data analysis.

## Quick Start

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

See `CODEBASE.md` for detailed module documentation.

## Requirements

- Python 3.8+
- OpenAI and/or Mistral API access
- Dependencies: `openai`, `mistralai`, `python-dotenv`
