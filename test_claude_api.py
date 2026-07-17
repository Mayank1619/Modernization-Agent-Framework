from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError


def load_local_dotenv(repo_root: Path) -> None:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple Claude API connectivity test")
    parser.add_argument(
        "--model",
        default=None,
        help="Claude model ID (defaults to AGENTIC_CLAUDE_MODEL or claude-haiku-4-5-20251001)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Claude API base URL (defaults to AGENTIC_CLAUDE_BASE_URL or https://api.anthropic.com)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Claude API key (defaults to AGENTIC_CLAUDE_API_KEY)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    load_local_dotenv(repo_root)

    model = (args.model or os.getenv("AGENTIC_CLAUDE_MODEL", "claude-haiku-4-5-20251001")).strip()
    base_url = (args.base_url or os.getenv("AGENTIC_CLAUDE_BASE_URL", "https://api.anthropic.com")).strip()
    api_key = (args.api_key or os.getenv("AGENTIC_CLAUDE_API_KEY", "")).strip()

    if not api_key:
        print("ERROR: Missing Claude key. Set AGENTIC_CLAUDE_API_KEY or pass --api-key.")
        return 1

    payload = {
        "model": model,
        "max_tokens": 120,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Reply with exactly: CLAUDE_API_OK"}],
            }
        ],
    }

    req = request.Request(
        url=f"{base_url.rstrip('/')}/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="ignore")
        print(f"ERROR: Claude API HTTP {exc.code}")
        print(err_body)
        return 2
    except URLError as exc:
        print("ERROR: Network or DNS failure while contacting Claude API")
        print(str(exc))
        return 3

    parts = []
    for block in body.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))

    text = "\n".join(part for part in parts if part.strip()).strip()

    print("SUCCESS: Claude API responded")
    print(f"Model: {model}")
    print("Response preview:")
    print(text[:400] if text else "<empty>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
