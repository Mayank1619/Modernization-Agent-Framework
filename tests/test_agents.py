from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from agents.legacy_analysis_agent import LegacyAnalysisAgent  # noqa: E402


def test_agent_initialization(tmp_path: Path) -> None:
    templates = FRAMEWORK_ROOT / "templates"
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()

    agent = LegacyAnalysisAgent(
        templates_dir=templates,
        input_root=input_root,
        output_root=output_root,
        dry_run=True,
    )
    assert agent.name == "LegacyAnalysisAgent"
    assert agent.prompt_template == "legacy_analysis_prompt.md"
    assert "program-analysis.md" in agent.output_files


def test_agent_creates_output_artifact(tmp_path: Path) -> None:
    templates = FRAMEWORK_ROOT / "templates"
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    (input_root / "cobol").mkdir(parents=True)
    output_root.mkdir()
    (input_root / "cobol" / "APP.cbl").write_text(
        "IDENTIFICATION DIVISION. PROGRAM-ID. APP.", encoding="utf-8"
    )

    agent = LegacyAnalysisAgent(
        templates_dir=templates,
        input_root=input_root,
        output_root=output_root,
        dry_run=False,
    )

    result = agent.run({"pipeline_name": "test"})
    assert result.outputs
    artifact = output_root / "program-analysis.md"
    assert artifact.exists()
    text = artifact.read_text(encoding="utf-8")
    assert "LegacyAnalysisAgent" in text
