from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from orchestrator.config import load_pipeline_config  # noqa: E402
from orchestrator.pipeline import PipelineRunner  # noqa: E402

import time


def test_mainframe_pipeline_dry_run(tmp_path: Path) -> None:
    input_root = tmp_path / "legacy"
    output_root = tmp_path / "output"
    (input_root / "cobol").mkdir(parents=True)
    (input_root / "copybooks").mkdir(parents=True)
    (input_root / "cobol" / "INQACC01.cbl").write_text(
        "IDENTIFICATION DIVISION. PROGRAM-ID. INQACC01.", encoding="utf-8"
    )
    (input_root / "copybooks" / "ACCTREC.cpy").write_text(
        "01 ACCOUNT-RECORD. 05 ACCOUNT-ID PIC X(12).", encoding="utf-8"
    )

    config = load_pipeline_config(
        FRAMEWORK_ROOT / "pipelines" / "mainframe_modernization.yaml"
    )
    runner = PipelineRunner(
        pipeline=config,
        templates_dir=FRAMEWORK_ROOT / "templates",
        input_root=input_root,
        output_root=output_root,
        dry_run=True,
    )
    runner.run()

    expected = [
        "program-analysis.md",
        "business-rules.md",
        "intended-system.md",
        "requirements.md",
        "spec.md",
        "plan.md",
        "tasks.md",
        "mapping-matrix.md",
        "test-spec.md",
        "openapi.yaml",
        "copilot-build-prompt.md",
        "qa-review-checklist.md",
        "code-review-checklist.md",
        "modernization-report.md",
    ]
    for name in expected:
        path = output_root / name
        assert path.exists(), f"Missing expected artifact: {name}"

    dry_run_text = (output_root / "program-analysis.md").read_text(encoding="utf-8")
    assert "DRY RUN" in dry_run_text


class FakeLlmClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "AI GENERATED CONTENT"


def test_mainframe_pipeline_with_ai_client(tmp_path: Path) -> None:
    input_root = tmp_path / "legacy"
    output_root = tmp_path / "output"
    (input_root / "cobol").mkdir(parents=True)
    (input_root / "copybooks").mkdir(parents=True)
    (input_root / "cobol" / "INQACC01.cbl").write_text(
        "IDENTIFICATION DIVISION. PROGRAM-ID. INQACC01.", encoding="utf-8"
    )
    (input_root / "copybooks" / "ACCTREC.cpy").write_text(
        "01 ACCOUNT-RECORD. 05 ACCOUNT-ID PIC X(12).", encoding="utf-8"
    )

    config = load_pipeline_config(
        FRAMEWORK_ROOT / "pipelines" / "mainframe_modernization.yaml"
    )
    runner = PipelineRunner(
        pipeline=config,
        templates_dir=FRAMEWORK_ROOT / "templates",
        input_root=input_root,
        output_root=output_root,
        dry_run=False,
        llm_client=FakeLlmClient(),
    )
    runner.run()

    artifact = output_root / "program-analysis.md"
    assert artifact.exists()
    assert artifact.read_text(encoding="utf-8") == "AI GENERATED CONTENT"


def test_demo_mode_injects_delay_for_each_agent(monkeypatch, tmp_path: Path) -> None:
    input_root = tmp_path / "legacy"
    output_root = tmp_path / "output"
    (input_root / "cobol").mkdir(parents=True)
    (input_root / "copybooks").mkdir(parents=True)
    (input_root / "cobol" / "INQACC01.cbl").write_text(
        "IDENTIFICATION DIVISION. PROGRAM-ID. INQACC01.", encoding="utf-8"
    )
    (input_root / "copybooks" / "ACCTREC.cpy").write_text(
        "01 ACCOUNT-RECORD. 05 ACCOUNT-ID PIC X(12).", encoding="utf-8"
    )

    config = load_pipeline_config(
        FRAMEWORK_ROOT / "pipelines" / "mainframe_modernization.yaml"
    )

    sleep_calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    runner = PipelineRunner(
        pipeline=config,
        templates_dir=FRAMEWORK_ROOT / "templates",
        input_root=input_root,
        output_root=output_root,
        dry_run=True,
        extra_context={"demo_delay_seconds": "2"},
    )
    runner.run()

    assert sleep_calls, "Expected demo mode to call sleep at least once"
    assert all(call == 2.0 for call in sleep_calls)
    assert len(sleep_calls) == len([step for step in config.agents if step.enabled])
