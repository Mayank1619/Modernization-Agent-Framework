from __future__ import annotations

from typing import Protocol


class LlmClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from prompts."""
