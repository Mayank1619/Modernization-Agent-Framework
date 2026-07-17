from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict
from urllib.error import HTTPError
from urllib import request

from llm.client import LlmClient


CONTENT_TYPE_JSON = "application/json"


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
                "Content-Type": CONTENT_TYPE_JSON,
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            raise ValueError(
                f"OpenAI-compatible API request failed with status {exc.code}: {body}"
            ) from exc

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
                "Content-Type": CONTENT_TYPE_JSON,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            raise ValueError(f"Ollama API request failed with status {exc.code}: {body}") from exc

        content = data.get("response", "")
        if not content.strip():
            raise ValueError("Ollama API returned empty content.")

        return content.strip()


@dataclass
class ClaudeClient(LlmClient):
    base_url: str
    model: str
    api_key: str
    timeout_seconds: int = 120

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
            "max_tokens": 4096,
        }

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url.rstrip('/')}/v1/messages",
            data=body,
            headers={
                "Content-Type": CONTENT_TYPE_JSON,
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            raise ValueError(
                f"Claude API request failed with status {exc.code}: {body}"
            ) from exc

        content_blocks = data.get("content", [])
        text_parts = [
            block.get("text", "")
            for block in content_blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        content = "\n".join(part for part in text_parts if part.strip())
        if not content.strip():
            raise ValueError("Claude API returned empty content.")

        return content.strip()
