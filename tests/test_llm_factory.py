from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from llm.factory import LlmSettings, build_llm_client  # noqa: E402
from llm.http_clients import ClaudeClient  # noqa: E402


def test_build_claude_client() -> None:
    settings = LlmSettings(
        enabled=True,
        provider="claude",
        model="claude-3-5-sonnet-latest",
        base_url="https://api.anthropic.com",
        api_key="test-key",
        timeout_seconds=30,
    )
    client = build_llm_client(settings)
    assert isinstance(client, ClaudeClient)
    assert client.model == "claude-3-5-sonnet-latest"
