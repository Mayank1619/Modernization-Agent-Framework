from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from llm.client import LlmClient
from llm.http_clients import ClaudeClient, OllamaClient, OpenAiCompatibleClient


@dataclass
class LlmSettings:
    enabled: bool
    provider: str
    model: str
    base_url: str
    api_key: str
    timeout_seconds: int
    max_output_tokens: Optional[int] = None


def _parse_optional_positive_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = int(text)
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def load_llm_settings() -> LlmSettings:
    enabled = os.getenv("AGENTIC_AI_ENABLED", "false").lower() == "true"
    provider = os.getenv("AGENTIC_AI_PROVIDER", "ollama").lower()
    model = os.getenv("AGENTIC_AI_MODEL", "llama3.1")
    default_base_url = "http://localhost:11434"
    if provider == "claude":
        default_base_url = "https://api.anthropic.com"
    base_url = os.getenv("AGENTIC_AI_BASE_URL", default_base_url)
    api_key = os.getenv("AGENTIC_AI_API_KEY", "")
    timeout_seconds = int(os.getenv("AGENTIC_AI_TIMEOUT_SECONDS", "120"))
    max_output_tokens = _parse_optional_positive_int(
        os.getenv("AGENTIC_AI_MAX_OUTPUT_TOKENS", "")
    )
    return LlmSettings(
        enabled=enabled,
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
        max_output_tokens=max_output_tokens,
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
            max_output_tokens=settings.max_output_tokens,
        )

    if settings.provider == "claude":
        if not settings.api_key:
            raise ValueError("AGENTIC_AI_API_KEY is required for provider=claude")
        return ClaudeClient(
            base_url=settings.base_url,
            model=settings.model,
            api_key=settings.api_key,
            timeout_seconds=settings.timeout_seconds,
            max_output_tokens=settings.max_output_tokens or 4096,
        )

    raise ValueError(f"Unsupported AGENTIC_AI_PROVIDER: {settings.provider}")
