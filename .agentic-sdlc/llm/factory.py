from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from llm.client import LlmClient
from llm.http_clients import OllamaClient, OpenAiCompatibleClient


@dataclass
class LlmSettings:
    enabled: bool
    provider: str
    model: str
    base_url: str
    api_key: str
    timeout_seconds: int


def load_llm_settings() -> LlmSettings:
    enabled = os.getenv("AGENTIC_AI_ENABLED", "false").lower() == "true"
    provider = os.getenv("AGENTIC_AI_PROVIDER", "ollama").lower()
    model = os.getenv("AGENTIC_AI_MODEL", "llama3.1")
    base_url = os.getenv("AGENTIC_AI_BASE_URL", "http://localhost:11434")
    api_key = os.getenv("AGENTIC_AI_API_KEY", "")
    timeout_seconds = int(os.getenv("AGENTIC_AI_TIMEOUT_SECONDS", "120"))
    return LlmSettings(
        enabled=enabled,
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )


def build_llm_client(settings: LlmSettings) -> Optional[LlmClient]:
    if not settings.enabled:
        return None

    if settings.provider == "ollama":
        return OllamaClient(
            base_url=settings.base_url,
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
        )

    if settings.provider == "openai":
        if not settings.api_key:
            raise ValueError("AGENTIC_AI_API_KEY is required for provider=openai")
        return OpenAiCompatibleClient(
            base_url=settings.base_url,
            model=settings.model,
            api_key=settings.api_key,
            timeout_seconds=settings.timeout_seconds,
        )

    raise ValueError(f"Unsupported AGENTIC_AI_PROVIDER: {settings.provider}")
