from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict
from urllib import request

from llm.client import LlmClient


@dataclass
class OpenAiCompatibleClient(LlmClient):
    base_url: str
    model: str
    api_key: str
    timeout_seconds: int = 120

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url.rstrip('/')}/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=self.timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        choices = data.get("choices", [])
        if not choices:
            raise ValueError("OpenAI-compatible API returned no choices.")

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not content.strip():
            raise ValueError("OpenAI-compatible API returned empty content.")

        return content.strip()


@dataclass
class OllamaClient(LlmClient):
    base_url: str
    model: str
    timeout_seconds: int = 120

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "options": {
                "temperature": 0.2,
            },
        }

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url.rstrip('/')}/api/generate",
            data=body,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=self.timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        content = data.get("response", "")
        if not content.strip():
            raise ValueError("Ollama API returned empty content.")

        return content.strip()
