from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from llm.client import LlmClient
from orchestrator.pipeline import PipelineRunner


@dataclass
class ArtifactComparison:
    name: str
    status: str
    selected_source: str
    rationale: str
    primary_chars: int
    secondary_chars: int
    merged_chars: int


CORE_MERGE_ARTIFACTS = {
    "business-rules.md",
    "requirements.md",
    "spec.md",
    "mapping-matrix.md",
    "traceability-matrix.md",
    "test-spec.md",
    "openapi.yaml",
}


def _read_text_if_exists(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _list_artifact_names(primary_output: Path, secondary_output: Path) -> List[str]:
    names = {
        file_path.name
        for root in (primary_output, secondary_output)
        for file_path in root.glob("*")
        if file_path.is_file() and file_path.suffix.lower() in {".md", ".yaml", ".yml"}
    }
    return sorted(names)


def _merge_with_llm(
    artifact_name: str,
    primary_text: str,
    secondary_text: str,
    merge_client: LlmClient,
) -> str:
    system_prompt = (
        "You are a strict spec modernization artifact merger. "
        "Produce a single best artifact by combining two versions. "
        "Keep the same output format as the artifact type, preserve factual correctness, "
        "do not invent fields not present in legacy or spec inputs, and maximize useful detail."
    )
    user_prompt = (
        f"Artifact: {artifact_name}\n\n"
        "Version A (primary model output):\n"
        f"{primary_text}\n\n"
        "Version B (secondary model output):\n"
        f"{secondary_text}\n\n"
        "Merge instructions:\n"
        "1) Keep all non-conflicting detail from both versions.\n"
        "2) Resolve conflicts in favor of factual consistency and traceability.\n"
        "3) Keep IDs stable and explicit where possible (FR/AC/TC/BR/TASK).\n"
        "4) Return only final artifact content with no explanations.\n"
    )
    return merge_client.generate(system_prompt=system_prompt, user_prompt=user_prompt)


def _markdown_heading_score(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))


def _table_score(text: str) -> int:
    return sum(1 for line in text.splitlines() if "|" in line)


def _heuristic_select(primary_text: str, secondary_text: str) -> tuple[str, str]:
    primary_score = len(primary_text) + (_markdown_heading_score(primary_text) * 100) + (
        _table_score(primary_text) * 40
    )
    secondary_score = len(secondary_text) + (
        _markdown_heading_score(secondary_text) * 100
    ) + (_table_score(secondary_text) * 40)

    if secondary_score > primary_score:
        return secondary_text, "secondary"
    return primary_text, "primary"


def merge_dual_outputs(
    primary_output: Path,
    secondary_output: Path,
    merged_output: Path,
    merge_client: LlmClient | None,
) -> List[ArtifactComparison]:
    merged_output.mkdir(parents=True, exist_ok=True)
    comparisons: List[ArtifactComparison] = []

    for artifact_name in _list_artifact_names(primary_output, secondary_output):
        primary_path = primary_output / artifact_name
        secondary_path = secondary_output / artifact_name
        merged_path = merged_output / artifact_name

        primary_text = _read_text_if_exists(primary_path)
        secondary_text = _read_text_if_exists(secondary_path)

        if primary_text and not secondary_text:
            merged_text = primary_text
            status = "missing-secondary"
            selected_source = "primary"
            rationale = "Artifact missing in secondary output."
        elif secondary_text and not primary_text:
            merged_text = secondary_text
            status = "missing-primary"
            selected_source = "secondary"
            rationale = "Artifact missing in primary output."
        elif primary_text == secondary_text:
            merged_text = primary_text
            status = "identical"
            selected_source = "both"
            rationale = "Both model outputs are identical."
        else:
            if artifact_name in CORE_MERGE_ARTIFACTS and merge_client is not None:
                merged_text = _merge_with_llm(
                    artifact_name=artifact_name,
                    primary_text=primary_text,
                    secondary_text=secondary_text,
                    merge_client=merge_client,
                )
                status = "merged"
                selected_source = "llm-merge"
                rationale = "Combined non-overlapping detail and resolved conflicts."
            else:
                merged_text, selected_source = _heuristic_select(
                    primary_text=primary_text,
                    secondary_text=secondary_text,
                )
                status = "selected"
                rationale = (
                    "Selected higher-detail variant using markdown/table/length heuristic."
                )

        merged_path.write_text(merged_text, encoding="utf-8")
        comparisons.append(
            ArtifactComparison(
                name=artifact_name,
                status=status,
                selected_source=selected_source,
                rationale=rationale,
                primary_chars=len(primary_text),
                secondary_chars=len(secondary_text),
                merged_chars=len(merged_text),
            )
        )

    report_lines = [
        "# Dual-Model Comparison Analysis",
        "",
        "This report compares primary-model and Claude-model artifacts and records how final outputs were selected.",
        "",
        "| Artifact | Status | Selected | Primary chars | Claude chars | Merged chars | Notes |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for item in comparisons:
        report_lines.append(
            f"| {item.name} | {item.status} | {item.selected_source} | "
            f"{item.primary_chars} | {item.secondary_chars} | {item.merged_chars} | {item.rationale} |"
        )

    (merged_output / "dual-model-analysis.md").write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    return comparisons


def run_pipeline_dual_model(
    *,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    primary_client: LlmClient | None,
    secondary_client: LlmClient | None,
    extra_context: Dict[str, str] | None = None,
    event_sink: Callable[[Dict[str, object]], None] | None = None,
    parallel: bool = True,
    primary_dry_run: bool = False,
    secondary_dry_run: bool = False,
    use_llm_merge: bool = True,
) -> List[ArtifactComparison]:
    primary_output = output_root.parent / f"{output_root.name}_primary"
    secondary_output = output_root.parent / f"{output_root.name}_claude"

    def _runner_for_phase(phase: str) -> PipelineRunner:
        is_primary = phase == "primary"
        return PipelineRunner(
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            output_root=primary_output if is_primary else secondary_output,
            dry_run=primary_dry_run if is_primary else secondary_dry_run,
            llm_client=primary_client if is_primary else secondary_client,
            extra_context=extra_context,
            event_sink=(
                None
                if event_sink is None
                else lambda event: event_sink({"phase": phase, **event})
            ),
        )

    def _run_phase(phase: str) -> None:
        _runner_for_phase(phase).run()

    if parallel:
        if event_sink is not None:
            event_sink({"event": "phase_started", "phase": "primary"})
            event_sink({"event": "phase_started", "phase": "claude"})

        phase_by_future = {}
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="dual-run") as executor:
            phase_by_future[executor.submit(_run_phase, "primary")] = "primary"
            phase_by_future[executor.submit(_run_phase, "claude")] = "claude"

            pending = set(phase_by_future.keys())
            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    phase = phase_by_future[future]
                    # Re-raise any runner exception immediately.
                    future.result()
                    if event_sink is not None:
                        event_sink({"event": "phase_completed", "phase": phase})
    else:
        if event_sink is not None:
            event_sink({"event": "phase_started", "phase": "primary"})

        _run_phase("primary")

        if event_sink is not None:
            event_sink({"event": "phase_completed", "phase": "primary"})
            event_sink({"event": "phase_started", "phase": "claude"})

        _run_phase("claude")

        if event_sink is not None:
            event_sink({"event": "phase_completed", "phase": "claude"})

    if event_sink is not None:
        event_sink({"event": "merge_started", "phase": "merge"})

    comparisons = merge_dual_outputs(
        primary_output=primary_output,
        secondary_output=secondary_output,
        merged_output=output_root,
        merge_client=primary_client if use_llm_merge else None,
    )
    if event_sink is not None:
        event_sink(
            {
                "event": "merge_completed",
                "phase": "merge",
                "artifacts_compared": len(comparisons),
            }
        )
    return comparisons
