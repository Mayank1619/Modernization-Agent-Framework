from __future__ import annotations

from typing import Any
from typing import Protocol


class LlmClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from prompts."""

    def get_last_usage(self) -> dict[str, Any] | None:
        """Return provider-reported token usage for the most recent generation."""
