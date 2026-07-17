from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from orchestrator.config import load_pipeline_config  # noqa: E402
from orchestrator.pipeline import PipelineRunner  # noqa: E402


def test_pipeline_emits_run_and_agent_events(tmp_path: Path) -> None:
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

    events = []
    runner = PipelineRunner(
        pipeline=config,
        templates_dir=FRAMEWORK_ROOT / "templates",
        input_root=input_root,
        output_root=output_root,
        dry_run=True,
        event_sink=lambda event: events.append(event),
    )

    runner.run()

    event_names = [item["event"] for item in events]
    assert "run_started" in event_names
    assert "agent_started" in event_names
    assert "agent_completed" in event_names
    assert event_names[-1] == "run_completed"
