from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_detail_drift import (  # noqa: E402
    ValidationThresholds,
    build_report,
    validate_artifact,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_artifact_passes_when_within_thresholds(tmp_path: Path) -> None:
    baseline_dir = tmp_path / "bundle" / "specs"
    generated_dir = tmp_path / "output"

    baseline = "# Spec\n\n## Requirements\n- FR-001\n- AC-001\n"
    generated = "# Spec\n\n## Requirements\n- FR-001\n- AC-001\n- TASK-001\n"
    _write(baseline_dir / "spec.md", baseline)
    _write(generated_dir / "spec.md", generated)

    thresholds = ValidationThresholds(
        min_char_ratio=0.75,
        max_char_ratio=1.5,
        min_heading_ratio=0.6,
        max_heading_ratio=1.6,
        min_id_ratio=0.5,
        max_id_ratio=2.0,
    )

    result = validate_artifact(
        artifact="spec.md",
        baseline_dir=baseline_dir,
        generated_dir=generated_dir,
        thresholds=thresholds,
    )

    assert result.status == "pass"
    assert result.reasons == []


def test_validate_artifact_fails_when_too_short(tmp_path: Path) -> None:
    baseline_dir = tmp_path / "bundle" / "specs"
    generated_dir = tmp_path / "output"

    baseline = "# Spec\n\n## Rules\n- FR-001\n- AC-001\n- TC-001\n"
    generated = "# Spec\n"
    _write(baseline_dir / "spec.md", baseline)
    _write(generated_dir / "spec.md", generated)

    thresholds = ValidationThresholds(
        min_char_ratio=0.8,
        max_char_ratio=1.4,
        min_heading_ratio=0.8,
        max_heading_ratio=1.4,
        min_id_ratio=0.8,
        max_id_ratio=1.4,
    )

    result = validate_artifact(
        artifact="spec.md",
        baseline_dir=baseline_dir,
        generated_dir=generated_dir,
        thresholds=thresholds,
    )

    assert result.status == "fail"
    assert any("chars ratio too low" in reason for reason in result.reasons)


def test_build_report_contains_summary() -> None:
    thresholds = ValidationThresholds(
        min_char_ratio=0.75,
        max_char_ratio=1.35,
        min_heading_ratio=0.7,
        max_heading_ratio=1.6,
        min_id_ratio=0.7,
        max_id_ratio=1.6,
    )

    report = build_report(results=[], thresholds=thresholds)

    assert "Detail Drift Validation Report" in report
    assert "Summary" in report
