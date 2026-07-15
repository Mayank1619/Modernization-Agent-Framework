from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from orchestrator.config import load_pipeline_config  # noqa: E402


def test_load_pipeline_config() -> None:
    config = load_pipeline_config(
        FRAMEWORK_ROOT / "pipelines" / "mainframe_modernization.yaml"
    )
    assert config.name == "mainframe_modernization"
    assert len(config.agents) >= 13
    assert config.agents[0].name == "LegacyAnalysisAgent"
