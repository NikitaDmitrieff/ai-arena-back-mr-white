# Codebase Architecture Documentation

Detailed technical documentation for the Mister White AI Tournament system.

## Overview

The codebase implements a modular AI tournament system for the social deduction game "Mister White". The architecture is designed for extensibility, maintainability, and comprehensive data analysis.

## Module Breakdown

### Organized Folder Structure

The codebase is organized into logical packages within the `src/` directory for better maintainability:

- **`src/core/`**: Core game engine components (game logic, AI agents, data models)
- **`src/config/`**: Configuration management and constants
- **`src/simulation/`**: Tournament orchestration and multi-game management
- **`src/data/`**: Data export, persistence, and analysis display
- **`src/prompts/`**: Game prompts and AI instructions

This structure provides clear separation of concerns and makes the codebase easier to navigate and extend.

### Core Architecture

```
main.py (main entry point)
└── src/
    ├── config/
    │   ├── config.py (load configuration)
    │   └── constants.py (defaults and constants)
    ├── core/
    │   ├── agent.py (LLM players)
    │   ├── game.py (execute single games)
    │   └── models.py (data structures)
    ├── simulation/
    │   └── tournament.py (orchestrate games)
    ├── data/
    │   ├── data_export.py (save results)
    │   └── results.py (display analysis)
    └── prompts/
        └── prompts.py (game text and instructions)
```

## Detailed Module Documentation

### `main.py` - Entry Point
**Purpose**: High-level tournament orchestration and user interface

**Key Functions**:
- `main()`: Primary entry point that coordinates entire tournament flow

**Responsibilities**:
- Load configuration from JSON
- Initialize and run tournament
- Save results to CSV
- Display final analysis
- Handle high-level error reporting

**Data Flow**: Configuration → Tournament → Results → Export

---

### `src/config/config.py` - Configuration Management
**Purpose**: Centralized configuration loading and validation

**Key Functions**:
- `load_simulation_config(config_path)`: Load and parse simulation_config.json

**Returns**: Tuple of (enabled_models, folder_config, tournament_config)

**Features**:
- JSON schema validation
- Fallback to defaults on errors
- Model format conversion
- Configuration merging

**Error Handling**: Graceful fallback to constants on file/JSON errors

---

### `src/core/game.py` - Core Game Engine
**Purpose**: Complete single game execution and mechanics

**Key Classes**:
- `MisterWhiteGame`: Game state and rule management

**Key Functions**:
- `play_single_game()`: Execute complete game with all phases

**Game Phases Implemented**:
1. **Setup**: Player assignment, role distribution, word selection
2. **Word Phase**: Strategic clue collection (regular players first, then Mister White)
3. **Discussion Phase**: 2 rounds of role-aware suspicion discussion with win-condition focus
4. **Voting Phase**: Strategic elimination voting with randomized context and role-specific prompts
5. **Results**: Winner determination and data collection

**Data Structures**:
- Game state tracking
- Message history with phase tagging
- Player information and role assignments
- Vote tallying and analysis

**Key Features**:
- **Deterministic role assignment**: Even distribution with Emily always as Mister White
- **Strategic prompting**: Role-specific prompts with explicit win conditions
- **Bias mitigation**: Randomized message order in voting to prevent timing-based decisions
- **Context-aware prompting**: Different information given to Citizens vs Mister White
- Comprehensive message logging with phase tracking
- Verbose mode for debugging strategic decisions

---

### `src/simulation/tournament.py` - Multi-Game Management
**Purpose**: Execute multiple games and aggregate statistics

**Key Functions**:
- `run_tournament()`: Execute series of games with statistics collection

**Statistics Tracked**:
- Per-model performance metrics
- Win rates by role (Mister White vs Citizen)
- Survival rates and elimination patterns
- Voting behavior analysis
- Cross-game performance trends

**Features**:
- Progress reporting
- Reproducible seeding
- Comprehensive model comparison
- Statistical aggregation

---

### `src/core/models.py` - Data Structures
**Purpose**: Type definitions and data containers

**Key Types**:
- `GameResult`: NamedTuple containing complete game outcome data

**Data Fields**:
- Game metadata (ID, timestamp)
- Player information and models
- Game outcome (winner, eliminated player)  
- Vote counts and patterns
- Complete message history
- Model attribution

**Design Philosophy**: Immutable data structures for reliable analysis

---

### `src/core/agent.py` - AI Player Implementation
**Purpose**: LLM integration and player behavior

**Key Classes**:
- `BaseAgent`: Core LLM interaction functionality
- `Player`: Game-specific player implementation

**Provider Support**:
- OpenAI (GPT models)
- Mistral (Mistral models)

**Features**:
- Multi-provider LLM integration
- Configurable model parameters
- Response API with fallbacks
- Error handling and retries

**Player Capabilities**:
- Role-aware behavior
- Context processing
- Strategic reasoning

---

### `src/prompts/prompts.py` - Strategic Game Prompts
**Purpose**: Centralized prompt management for competitive AI behavior with explicit win conditions

**Prompt Categories**:
1. **Clue Phase Prompts**:
   - **Citizens**: Strategic clue giving that balances helping allies vs confusing enemies
   - **Mister White**: Survival-focused blending with context analysis
   - Explicit explanation of the strategic tradeoff between obvious vs obscure clues

2. **Discussion Phase Prompts**:
   - **Role-aware**: Different prompts for Citizens vs Mister White
   - **Win-condition focused**: Emphasizes winning strategies for each role
   - **Evidence analysis**: Guides players to analyze clue connections properly

3. **Voting Phase Prompts**:
   - **Role-specific**: Separate prompts for Citizens and Mister White with different win conditions
   - **Strategic voting**: Emphasizes survival for Mister White, elimination for Citizens
   - **Anti-bias mechanisms**: Warns against order-based and repeated-word fallacies

**Strategic Enhancements**:
- **Win condition clarity**: Every prompt explains how to win in that role
- **Message randomization**: Voting context shuffled to remove timing biases
- **Strategic guidance**: Explains tradeoffs and optimal play patterns
- **Bias mitigation**: Addresses common logical fallacies in social deduction games

---

### `src/data/data_export.py` - Data Persistence
**Purpose**: Comprehensive CSV export with organized file structure

**Export Formats**:
1. **Games CSV**: High-level game outcomes and metadata
2. **Players CSV**: Per-player performance and characteristics  
3. **Messages CSV**: Complete conversation logs with provider/model attribution
4. **Model Stats CSV**: Aggregated model performance metrics

**Features**:
- Organized folder structure with timestamps
- Custom naming support
- Model count integration
- UTF-8 encoding for international content
- **Enhanced Messages CSV**: Includes provider and model columns for each message
- Comprehensive data coverage with model attribution

**Messages CSV Structure**:
Fields: `game_id`, `provider`, `model`, `player_name`, `message_type`, `phase`, `round`, `content`, `secret_word`, `is_mister_white`

**Folder Naming Pattern**:
`{date}_{time}_{games}games_{models}_{custom_suffix}/`

---

### `src/data/results.py` - Analysis and Display
**Purpose**: Console output formatting and statistical analysis

**Key Functions**:
- `print_tournament_results()`: Format and display comprehensive results

**Display Features**:
- Tournament summary statistics
- Model rankings by performance
- Detailed per-model breakdowns
- Win rate analysis by role
- Survival and elimination patterns

**Metrics Displayed**:
- Overall win rates
- Mister White specific performance
- Citizen role performance
- Survival rates
- Average votes received

---

### Supporting Files

#### `src/config/constants.py`
- Default model configurations
- Player name pools (Emily reserved for Mister White)
- Secret word lists
- Fallback configurations

#### `src/prompts/prompts.py`
- All game text and instructions
- System prompts for LLM guidance
- User prompts for specific actions
- Role-specific prompt variations

#### `simulation_config.json`
- Tournament parameters
- Model selection
- Folder naming preferences
- All configurable aspects

## Data Flow Architecture

```
Configuration Loading:
simulation_config.json → src/config/config.py → main.py

Game Execution:
main.py → src/simulation/tournament.py → src/core/game.py → src/core/agent.py
                                   ↓
                           src/core/models.py (data structures)
                                   ↓
                        src/prompts/prompts.py (AI instructions)

Data Export:
tournament results → src/data/data_export.py → CSV files

Analysis Display:
tournament results → src/data/results.py → console output
```

## Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Separation of Concerns**: Game logic, data handling, and display are separate
3. **Configurability**: All parameters externalized to JSON
4. **Extensibility**: Easy to add new models, prompts, or analysis
5. **Data Integrity**: Comprehensive logging for reproducibility
6. **Error Resilience**: Graceful fallbacks and error handling

## Extension Points

- **New LLM Providers**: Add to `src/core/agent.py` with API integration
- **Game Variants**: Modify `src/core/game.py` phases or rules
- **Analysis Methods**: Extend `src/data/results.py` with new metrics
- **Export Formats**: Add formats to `src/data/data_export.py`
- **Prompt Strategies**: Experiment with `src/prompts/prompts.py` variations

## Performance Considerations

- **Parallel Execution**: Currently sequential for deterministic results
- **Memory Usage**: Message history grows with game length
- **API Rate Limits**: Built-in delays and error handling
- **File I/O**: Efficient CSV writing with streaming

## Testing Strategy

- **Module Testing**: Each module can be tested independently
- **Configuration Testing**: JSON schema validation
- **Game Logic Testing**: Deterministic seeding for reproducibility
- **Integration Testing**: End-to-end tournament execution
- **Data Validation**: CSV output verification
