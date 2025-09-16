# Mister White AI Tournament

AI tournament system for the social deduction game "Mister White" using multiple LLM providers.

## Quick Start

1. **Set up API keys** in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   MISTRAL_API_KEY=your_key_here
   ```

2. **Configure models** in `model_config.json`:
   - Move models between `enabled_models` and `disabled_models`
   - Optionally set custom folder naming

3. **Run tournament**:
   ```bash
   python main.py
   ```

## Game Flow

- **5 AI players** per game (configurable)
- **Word Phase**: Players give clues, Mister White guesses blind
- **Discussion Phase**: 2 rounds of suspicion discussion  
- **Voting Phase**: Eliminate suspected Mister White
- **Result**: Citizens win if Mister White eliminated, otherwise Mister White wins

## Configuration

### Model Selection (`model_config.json`)
```json
{
  "enabled_models": [
    {"provider": "openai", "model": "gpt-4o-mini"},
    {"provider": "mistral", "model": "mistral-small-latest"}
  ]
}
```

### Folder Naming
```json
{
  "folder_naming": {
    "custom_folder_name": "my_experiment",
    "use_custom_only": true
  }
}
```

## Output

Results saved in organized CSV files:
- `results/{date_time}_{params}/`
  - `*_games.csv` - Game outcomes
  - `*_players.csv` - Player performance 
  - `*_messages.csv` - All conversations
  - `*_model_stats.csv` - Model statistics

## Requirements

- Python 3.8+
- OpenAI and/or Mistral API access
- Dependencies: `openai`, `mistralai`, `python-dotenv`
