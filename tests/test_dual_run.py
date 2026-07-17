from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from orchestrator.dual_run import merge_dual_outputs  # noqa: E402


class MergeClientStub:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if "spec.md" in user_prompt:
            return "# merged spec\n\ncombined"
        return "merged"


def test_merge_dual_outputs_creates_analysis(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    secondary = tmp_path / "secondary"
    merged = tmp_path / "merged"
    primary.mkdir()
    secondary.mkdir()

    (primary / "spec.md").write_text("# primary spec\n", encoding="utf-8")
    (secondary / "spec.md").write_text("# secondary spec\n", encoding="utf-8")
    (primary / "requirements.md").write_text("# req\n", encoding="utf-8")

    comparisons = merge_dual_outputs(
        primary_output=primary,
        secondary_output=secondary,
        merged_output=merged,
        merge_client=MergeClientStub(),
    )

    assert any(item.name == "spec.md" and item.status == "merged" for item in comparisons)
    assert any(
        item.name == "requirements.md" and item.status == "missing-secondary"
        for item in comparisons
    )
    assert (merged / "spec.md").exists()
    assert (merged / "dual-model-analysis.md").exists()


def test_merge_dual_outputs_uses_heuristic_for_non_core(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    secondary = tmp_path / "secondary"
    merged = tmp_path / "merged"
    primary.mkdir()
    secondary.mkdir()

    (primary / "plan.md").write_text("# Plan\n\nShort", encoding="utf-8")
    (secondary / "plan.md").write_text(
        "# Plan\n\n## Phase 1\n| A | B |\n|---|---|\n| x | y |",
        encoding="utf-8",
    )

    merge_dual_outputs(
        primary_output=primary,
        secondary_output=secondary,
        merged_output=merged,
        merge_client=MergeClientStub(),
    )

    merged_text = (merged / "plan.md").read_text(encoding="utf-8")
    assert "## Phase 1" in merged_text
