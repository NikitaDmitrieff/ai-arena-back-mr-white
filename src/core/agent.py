"""Mister White specific player implementation built on top of BaseAgent."""

from nikitas_agents.agents import BaseAgent


class Player(BaseAgent):
    """Represents an in-game LLM participant with Mister White metadata."""

    def __init__(
        self,
        name: str,
        description: str,
        word: str = "No word, you are mister white",
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        is_mister_white: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            provider=provider,
            model=model,
        )
        self.word = word
        self.is_mister_white = is_mister_white


__all__ = ["BaseAgent", "Player"]
