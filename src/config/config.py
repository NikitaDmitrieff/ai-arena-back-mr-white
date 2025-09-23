"""
Configuration management for Mister White tournaments.
Handles loading and parsing of simulation_config.json.
"""

import json
from typing import Dict, List, Tuple

from src.config import constants


def load_simulation_config(
    config_path: str = "simulation_config.json",
) -> Tuple[List[Tuple[str, str]], Dict[str, any], Dict[str, any]]:
    """Load model configuration, folder naming options, and tournament config from JSON file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Convert enabled models to the format expected by the game
        enabled_models = []
        for simulation_config in config.get("enabled_models", []):
            enabled_models.append(
                (simulation_config["provider"], simulation_config["model"])
            )

        if not enabled_models:
            print("⚠️  No enabled models found in config, falling back to constants")
            enabled_models = constants.PROVIDERS_AND_MODELS
        else:
            print(f"📋 Loaded {len(enabled_models)} enabled models from {config_path}")

        # Load folder naming configuration
        folder_config = config.get(
            "folder_naming",
            {
                "custom_folder_name": None,
                "folder_suffix": None,
                "use_custom_only": False,
            },
        )

        # Load tournament configuration
        tournament_config = config.get(
            "tournament_config",
            {
                "num_games": 2,
                "verbose": False,
                "show_progress": True,
            },
        )

        return enabled_models, folder_config, tournament_config

    except FileNotFoundError:
        print(f"⚠️  Config file {config_path} not found, using constants")
        return (
            constants.PROVIDERS_AND_MODELS,
            {},
            {
                "num_games": 2,
                "verbose": False,
                "show_progress": True,
            },
        )
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON in {config_path}, using constants")
        return (
            constants.PROVIDERS_AND_MODELS,
            {},
            {
                "num_games": 2,
                "verbose": False,
                "show_progress": True,
            },
        )
