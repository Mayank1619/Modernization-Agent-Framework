from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
import math
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


def _to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _estimate_tokens_from_text(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def _capture_merge_usage(
    *,
    merge_client: LlmClient,
    primary_text: str,
    secondary_text: str,
    merged_text: str,
) -> Dict[str, int]:
    usage = None
    if hasattr(merge_client, "get_last_usage"):
        try:
            usage = merge_client.get_last_usage()
        except Exception:
            usage = None

    if isinstance(usage, dict):
        prompt_tokens = _to_int(usage.get("prompt_tokens"))
        completion_tokens = _to_int(usage.get("completion_tokens"))
        total_tokens = _to_int(usage.get("total_tokens")) or (prompt_tokens + completion_tokens)
        estimated_tokens = total_tokens if total_tokens > 0 else 0
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_tokens": estimated_tokens,
        }

    estimated_prompt = _estimate_tokens_from_text(primary_text) + _estimate_tokens_from_text(
        secondary_text
    )
    estimated_completion = _estimate_tokens_from_text(merged_text)
    estimated_total = estimated_prompt + estimated_completion
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": estimated_total,
        "estimated_tokens": estimated_total,
    }


def _empty_usage() -> Dict[str, int]:
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_tokens": 0,
    }


def _add_usage(target: Dict[str, int], delta: Dict[str, int]) -> None:
    for key in target:
        target[key] += _to_int(delta.get(key))


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


def _resolve_artifact_merge(
    artifact_name: str,
    primary_text: str,
    secondary_text: str,
    merge_client: LlmClient | None,
) -> tuple[str, str, str, str, Dict[str, int]]:
    usage_delta = _empty_usage()

    if primary_text and not secondary_text:
        return (
            primary_text,
            "missing-secondary",
            "primary",
            "Artifact missing in secondary output.",
            usage_delta,
        )
    if secondary_text and not primary_text:
        return (
            secondary_text,
            "missing-primary",
            "secondary",
            "Artifact missing in primary output.",
            usage_delta,
        )
    if primary_text == secondary_text:
        return (
            primary_text,
            "identical",
            "both",
            "Both model outputs are identical.",
            usage_delta,
        )

    if artifact_name in CORE_MERGE_ARTIFACTS and merge_client is not None:
        merged_text = _merge_with_llm(
            artifact_name=artifact_name,
            primary_text=primary_text,
            secondary_text=secondary_text,
            merge_client=merge_client,
        )
        usage_delta = _capture_merge_usage(
            merge_client=merge_client,
            primary_text=primary_text,
            secondary_text=secondary_text,
            merged_text=merged_text,
        )
        return (
            merged_text,
            "merged",
            "llm-merge",
            "Combined non-overlapping detail and resolved conflicts.",
            usage_delta,
        )

    merged_text, selected_source = _heuristic_select(
        primary_text=primary_text,
        secondary_text=secondary_text,
    )
    return (
        merged_text,
        "selected",
        selected_source,
        "Selected higher-detail variant using markdown/table/length heuristic.",
        usage_delta,
    )


def merge_dual_outputs(
    primary_output: Path,
    secondary_output: Path,
    merged_output: Path,
    merge_client: LlmClient | None,
    include_token_usage: bool = False,
) -> List[ArtifactComparison] | tuple[List[ArtifactComparison], Dict[str, int]]:
    merged_output.mkdir(parents=True, exist_ok=True)
    comparisons: List[ArtifactComparison] = []
    merge_token_usage = _empty_usage()

    for artifact_name in _list_artifact_names(primary_output, secondary_output):
        primary_path = primary_output / artifact_name
        secondary_path = secondary_output / artifact_name
        merged_path = merged_output / artifact_name

        primary_text = _read_text_if_exists(primary_path)
        secondary_text = _read_text_if_exists(secondary_path)

        merged_text, status, selected_source, rationale, usage_delta = _resolve_artifact_merge(
            artifact_name=artifact_name,
            primary_text=primary_text,
            secondary_text=secondary_text,
            merge_client=merge_client,
        )
        _add_usage(merge_token_usage, usage_delta)

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

    if include_token_usage:
        return comparisons, merge_token_usage
    return comparisons


def _emit_event(
    event_sink: Callable[[Dict[str, object]], None] | None,
    event: Dict[str, object],
) -> None:
    if event_sink is not None:
        event_sink(event)


def _build_phase_runner(
    *,
    phase: str,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    primary_output: Path,
    secondary_output: Path,
    primary_client: LlmClient | None,
    secondary_client: LlmClient | None,
    primary_dry_run: bool,
    secondary_dry_run: bool,
    extra_context: Dict[str, str] | None,
    event_sink: Callable[[Dict[str, object]], None] | None,
) -> PipelineRunner:
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


def _run_dual_phases_parallel(
    run_phase: Callable[[str], None],
    event_sink: Callable[[Dict[str, object]], None] | None,
) -> None:
    _emit_event(event_sink, {"event": "phase_started", "phase": "primary"})
    _emit_event(event_sink, {"event": "phase_started", "phase": "claude"})

    phase_by_future = {}
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="dual-run") as executor:
        phase_by_future[executor.submit(run_phase, "primary")] = "primary"
        phase_by_future[executor.submit(run_phase, "claude")] = "claude"

        pending = set(phase_by_future.keys())
        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                phase = phase_by_future[future]
                future.result()
                _emit_event(event_sink, {"event": "phase_completed", "phase": phase})


def _run_dual_phases_sequential(
    run_phase: Callable[[str], None],
    event_sink: Callable[[Dict[str, object]], None] | None,
) -> None:
    _emit_event(event_sink, {"event": "phase_started", "phase": "primary"})
    run_phase("primary")
    _emit_event(event_sink, {"event": "phase_completed", "phase": "primary"})

    _emit_event(event_sink, {"event": "phase_started", "phase": "claude"})
    run_phase("claude")
    _emit_event(event_sink, {"event": "phase_completed", "phase": "claude"})


def _merge_outputs_with_events(
    *,
    primary_output: Path,
    secondary_output: Path,
    output_root: Path,
    primary_client: LlmClient | None,
    use_llm_merge: bool,
    event_sink: Callable[[Dict[str, object]], None] | None,
) -> List[ArtifactComparison]:
    _emit_event(event_sink, {"event": "merge_started", "phase": "merge"})
    comparisons, merge_usage = merge_dual_outputs(
        primary_output=primary_output,
        secondary_output=secondary_output,
        merged_output=output_root,
        merge_client=primary_client if use_llm_merge else None,
        include_token_usage=True,
    )
    _emit_event(
        event_sink,
        {
            "event": "merge_completed",
            "phase": "merge",
            "artifacts_compared": len(comparisons),
            "token_usage": merge_usage,
        },
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

    def _run_phase(phase: str) -> None:
        _build_phase_runner(
            phase=phase,
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            primary_output=primary_output,
            secondary_output=secondary_output,
            primary_client=primary_client,
            secondary_client=secondary_client,
            primary_dry_run=primary_dry_run,
            secondary_dry_run=secondary_dry_run,
            extra_context=extra_context,
            event_sink=event_sink,
        ).run()

    run_phases = _run_dual_phases_parallel if parallel else _run_dual_phases_sequential
    run_phases(_run_phase, event_sink)

    return _merge_outputs_with_events(
        primary_output=primary_output,
        secondary_output=secondary_output,
        output_root=output_root,
        primary_client=primary_client,
        use_llm_merge=use_llm_merge,
        event_sink=event_sink,
    )
