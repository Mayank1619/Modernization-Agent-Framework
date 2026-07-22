from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PRIMARY_PROMPT_RATE_PER_1K = 0.00015
PRIMARY_COMPLETION_RATE_PER_1K = 0.0006


@dataclass
class TunePreset:
    name: str
    max_sources: int
    preview_chars: int
    max_output_tokens: int


@dataclass
class TuneRunResult:
    preset: TunePreset
    output_dir: Path
    token_usage: Dict[str, int]
    estimated_cost: float
    quality_score: float


def _parse_optional_positive_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = int(text)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _load_env_file(env_path: Path, locked_keys: set[str]) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in locked_keys:
            os.environ[key] = value


def load_local_dotenv(repo_root: Path) -> None:
    # Precedence: process env > .env.local > .env
    locked_keys = set(os.environ.keys())
    _load_env_file(repo_root / ".env", locked_keys)
    _load_env_file(repo_root / ".env.local", locked_keys)


def parse_args() -> argparse.Namespace:
    default_pipeline = "mainframe_modernization"
    default_input = ".agentic-sdlc/examples/inqacc/legacy"
    default_output = ".agentic-sdlc/examples/inqacc/output"

    parser = argparse.ArgumentParser(
        description=(
            "Run local Agentic SDLC pipelines for spec-driven development and modernization. "
            "Defaults are configured for the mainframe modernization example."
        )
    )
    parser.add_argument(
        "--pipeline",
        default=default_pipeline,
        help=(
            "Pipeline name (without extension). "
            f"Default: {default_pipeline}."
        ),
    )
    parser.add_argument(
        "--input",
        default=default_input,
        help=(
            "Input folder containing legacy source and context documents. "
            f"Default: {default_input}."
        ),
    )
    parser.add_argument(
        "--output",
        default=default_output,
        help=(
            "Output folder where generated artifacts are written. "
            f"Default: {default_output}."
        ),
    )
    parser.add_argument(
        "--system-intent",
        default=None,
        help=(
            "Optional markdown file describing intended target system "
            "(stack, versions, security, frontend/backend constraints)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate placeholder artifacts without claiming implementation-ready content.",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Enable live AI generation via configured provider.",
    )
    parser.add_argument(
        "--ai-provider",
        choices=["ollama", "openai", "claude"],
        default=None,
        help="AI provider for live generation. Defaults to env AGENTIC_AI_PROVIDER.",
    )
    parser.add_argument(
        "--ai-model",
        default=None,
        help="Model name for AI generation. Defaults to env AGENTIC_AI_MODEL.",
    )
    parser.add_argument(
        "--ai-base-url",
        default=None,
        help="Base URL for AI provider API. Defaults to env AGENTIC_AI_BASE_URL.",
    )
    parser.add_argument(
        "--ai-api-key",
        default=None,
        help="API key for provider=openai. Defaults to env AGENTIC_AI_API_KEY.",
    )
    parser.add_argument(
        "--ai-max-output-tokens",
        type=int,
        default=None,
        help=(
            "Optional max completion tokens for primary provider responses. "
            "Defaults to env AGENTIC_AI_MAX_OUTPUT_TOKENS when set."
        ),
    )
    parser.add_argument(
        "--compare-with-claude",
        action="store_true",
        help=(
            "Run the same pipeline with both primary provider and Claude, then "
            "analyze and merge outputs into the final output folder."
        ),
    )
    parser.add_argument(
        "--demo-mode",
        action="store_true",
        help=(
            "Run a non-AI dual-phase demo (primary, claude, merge) using dry-run "
            "artifacts to visualize full execution flow without API keys."
        ),
    )
    parser.add_argument(
        "--parallel-dual-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable parallel execution of primary and Claude dual runs.",
    )
    parser.add_argument(
        "--optimize-tokens",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable compact context previews to reduce token usage and latency.",
    )
    parser.add_argument(
        "--token-max-sources",
        type=int,
        default=None,
        help="Max source files included in prompt context previews.",
    )
    parser.add_argument(
        "--token-preview-chars",
        type=int,
        default=None,
        help="Max characters per source preview in prompt context.",
    )
    parser.add_argument(
        "--claude-model",
        default=None,
        help="Claude model for secondary run. Defaults to env AGENTIC_CLAUDE_MODEL.",
    )
    parser.add_argument(
        "--claude-base-url",
        default=None,
        help=(
            "Claude API base URL for secondary run. "
            "Defaults to env AGENTIC_CLAUDE_BASE_URL or https://api.anthropic.com."
        ),
    )
    parser.add_argument(
        "--claude-api-key",
        default=None,
        help="Claude API key for secondary run. Defaults to env AGENTIC_CLAUDE_API_KEY.",
    )
    parser.add_argument(
        "--claude-max-output-tokens",
        type=int,
        default=None,
        help=(
            "Optional max completion tokens for Claude in dual-model mode. "
            "Defaults to env AGENTIC_CLAUDE_MAX_OUTPUT_TOKENS or AGENTIC_AI_MAX_OUTPUT_TOKENS."
        ),
    )
    parser.add_argument(
        "--auto-tune-tokens",
        action="store_true",
        help=(
            "Benchmark multiple token settings, score quality vs cost, and select the "
            "best configuration automatically."
        ),
    )
    parser.add_argument(
        "--auto-tune-quality-threshold",
        type=float,
        default=0.92,
        help=(
            "Minimum fraction of best quality score required for cost-based selection "
            "during token auto-tuning (0.0 to 1.0). Default: 0.92."
        ),
    )
    parser.epilog = (
        "Examples:\n"
        "  python run_pipeline.py\n"
        "  python run_pipeline.py --dry-run\n"
        "  python run_pipeline.py --use-ai --ai-provider ollama --ai-model llama3.1 "
        "--ai-base-url http://localhost:11434\n"
        "  python run_pipeline.py --use-ai --ai-provider openai --ai-model gpt-4o-mini "
        "--ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>\n"
        "  python run_pipeline.py --use-ai --ai-provider openai --compare-with-claude "
        "--claude-model claude-haiku-4-5-20251001\n"
        "  python run_pipeline.py --use-ai --auto-tune-tokens"
    )
    return parser.parse_args()


def build_claude_settings(args) -> Tuple[str, str, str, Optional[int]]:
    model = (
        args.claude_model
        or os.getenv("AGENTIC_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    ).strip()
    base_url = (args.claude_base_url or os.getenv(
        "AGENTIC_CLAUDE_BASE_URL", "https://api.anthropic.com"
    )).strip()
    api_key = (args.claude_api_key or os.getenv("AGENTIC_CLAUDE_API_KEY", "")).strip()
    max_output_tokens = args.claude_max_output_tokens
    if max_output_tokens is None:
        max_output_tokens = _parse_optional_positive_int(
            os.getenv("AGENTIC_CLAUDE_MAX_OUTPUT_TOKENS", "")
        )
    if max_output_tokens is None:
        max_output_tokens = _parse_optional_positive_int(
            os.getenv("AGENTIC_AI_MAX_OUTPUT_TOKENS", "")
        )
    if not api_key:
        raise ValueError(
            "Claude dual-run requires a key. Set --claude-api-key or AGENTIC_CLAUDE_API_KEY."
        )
    return model, base_url, api_key, max_output_tokens


def resolve_system_intent_path(args, repo_root: Path, framework_root: Path) -> str:
    if not args.system_intent:
        return ""

    requested_system_intent = (repo_root / args.system_intent).resolve()
    resolved_system_intent = requested_system_intent
    if not resolved_system_intent.exists():
        resolved_system_intent = (framework_root / args.system_intent).resolve()
    if not resolved_system_intent.exists() or not resolved_system_intent.is_file():
        raise FileNotFoundError(f"System intent file not found: {args.system_intent}")
    return str(resolved_system_intent)


def apply_ai_env_overrides(args) -> None:
    if args.demo_mode:
        os.environ["AGENTIC_AI_ENABLED"] = "false"
    elif args.use_ai:
        os.environ["AGENTIC_AI_ENABLED"] = "true"
    if args.ai_provider:
        os.environ["AGENTIC_AI_PROVIDER"] = args.ai_provider
    if args.ai_model:
        os.environ["AGENTIC_AI_MODEL"] = args.ai_model
    if args.ai_base_url:
        os.environ["AGENTIC_AI_BASE_URL"] = args.ai_base_url
    if args.ai_api_key:
        os.environ["AGENTIC_AI_API_KEY"] = args.ai_api_key
    if args.ai_max_output_tokens is not None:
        os.environ["AGENTIC_AI_MAX_OUTPUT_TOKENS"] = str(args.ai_max_output_tokens)


def apply_token_optimization_overrides(args) -> None:
    if not args.optimize_tokens:
        return

    if args.token_max_sources is not None:
        os.environ["AGENTIC_CONTEXT_MAX_SOURCES"] = str(args.token_max_sources)
    else:
        os.environ.setdefault("AGENTIC_CONTEXT_MAX_SOURCES", "12")

    if args.token_preview_chars is not None:
        os.environ["AGENTIC_CONTEXT_PREVIEW_CHARS"] = str(args.token_preview_chars)
    else:
        os.environ.setdefault("AGENTIC_CONTEXT_PREVIEW_CHARS", "1400")


def _run_single_model(
    *,
    args,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    llm_settings,
    llm_client,
    system_intent_path: str,
) -> int:
    from orchestrator.pipeline import PipelineRunner

    runner = PipelineRunner(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        dry_run=args.dry_run,
        llm_client=llm_client,
        extra_context={"system_intent_path": system_intent_path},
    )

    results = runner.run()
    print(f"Pipeline: {pipeline.name}")
    print(f"Description: {pipeline.description}")
    print(f"Dry run: {args.dry_run}")
    print(f"AI enabled: {llm_settings.enabled}")
    if llm_settings.enabled:
        print(
            "AI provider/model: "
            f"{llm_settings.provider}/{llm_settings.model} @ {llm_settings.base_url}"
        )
    for result in results:
        outputs = ", ".join(path.name for path in result.outputs)
        print(f"- {result.agent_name}: {outputs}")

    return 0 if results else 1


def _prepare_dual_clients(args, llm_settings, llm_client):
    from llm.factory import LlmSettings, build_llm_client

    if not args.demo_mode and (not llm_settings.enabled or llm_client is None):
        raise ValueError(
            "Dual-model comparison requires primary AI generation. "
            "Use --use-ai with a primary provider."
        )

    claude_model = "demo-claude"
    claude_base_url = "disabled"
    claude_client = None

    if not args.demo_mode:
        claude_model, claude_base_url, claude_api_key, claude_max_output_tokens = build_claude_settings(args)
        claude_client = build_llm_client(
            LlmSettings(
                enabled=True,
                provider="claude",
                model=claude_model,
                base_url=claude_base_url,
                api_key=claude_api_key,
                timeout_seconds=llm_settings.timeout_seconds,
                max_output_tokens=claude_max_output_tokens,
            )
        )
        if claude_client is None:
            raise ValueError("Failed to initialize Claude client for dual-model comparison")

    return claude_model, claude_base_url, claude_client


def _run_dual_model(
    *,
    args,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    llm_settings,
    llm_client,
    system_intent_path: str,
) -> int:
    from orchestrator.dual_run import run_pipeline_dual_model

    if args.dry_run and not args.demo_mode:
        raise ValueError("--compare-with-claude cannot be combined with --dry-run")
    if args.demo_mode and args.use_ai:
        print("[INFO] Demo mode enabled. Ignoring --use-ai and running dry-run dual phases.")

    claude_model, claude_base_url, claude_client = _prepare_dual_clients(
        args,
        llm_settings,
        llm_client,
    )

    comparisons = run_pipeline_dual_model(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        primary_client=None if args.demo_mode else llm_client,
        secondary_client=claude_client,
        extra_context={"system_intent_path": system_intent_path, "demo_delay_seconds": 2},
        parallel=args.parallel_dual_run,
        primary_dry_run=args.demo_mode,
        secondary_dry_run=args.demo_mode,
        use_llm_merge=not args.demo_mode,
    )

    print(f"Pipeline: {pipeline.name}")
    print(f"Description: {pipeline.description}")
    print(f"Dual-model comparison: {'demo mode' if args.demo_mode else 'enabled'}")
    print(f"Dual run parallel: {args.parallel_dual_run}")
    if args.demo_mode:
        print("Primary provider/model: demo/non-ai")
        print("Secondary provider/model: demo/non-ai")
    else:
        print(
            "Primary provider/model: "
            f"{llm_settings.provider}/{llm_settings.model} @ {llm_settings.base_url}"
        )
        print(f"Secondary provider/model: claude/{claude_model} @ {claude_base_url}")
    print(f"Merged output folder: {output_root}")
    print(
        "Additional artifacts: "
        f"{output_root.parent / (output_root.name + '_primary')}, "
        f"{output_root.parent / (output_root.name + '_claude')}, "
        f"{output_root / 'dual-model-analysis.md'}"
    )
    print(f"Artifacts compared: {len(comparisons)}")
    return 0 if comparisons else 1


def _sanitize_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower() or "preset"


def _sum_token_usage(results) -> Dict[str, int]:
    usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_tokens": 0,
    }
    for result in results:
        for key in usage:
            usage[key] += int(result.token_usage.get(key, 0) or 0)
    return usage


def _estimate_primary_cost(token_usage: Dict[str, int]) -> float:
    prompt_tokens = int(token_usage.get("prompt_tokens", 0) or 0)
    completion_tokens = int(token_usage.get("completion_tokens", 0) or 0)
    return (
        (prompt_tokens / 1000.0) * PRIMARY_PROMPT_RATE_PER_1K
        + (completion_tokens / 1000.0) * PRIMARY_COMPLETION_RATE_PER_1K
    )


def _score_artifact_quality(output_dir: Path) -> float:
    files = [
        path
        for path in sorted(output_dir.glob("*"))
        if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml"}
    ]
    if not files:
        return 0.0

    total_chars = 0
    heading_count = 0
    table_count = 0
    id_count = 0
    filled_files = 0

    id_pattern = re.compile(r"\b(?:FR|BR|NFR|AC|TC|TASK)-\d+\b", re.IGNORECASE)
    for file_path in files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        stripped = text.strip()
        if stripped:
            filled_files += 1
        total_chars += len(text)
        heading_count += sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))
        table_count += sum(1 for line in text.splitlines() if "|" in line)
        id_count += len(id_pattern.findall(text))

    completeness = filled_files / max(1, len(files))
    length_component = math.log10(max(total_chars, 10))
    structure_component = (heading_count * 0.18) + (table_count * 0.04)
    trace_component = id_count * 0.08
    completeness_component = completeness * 6.0
    return length_component + structure_component + trace_component + completeness_component


def _copy_selected_artifacts(source_dir: Path, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for path in destination_dir.glob("*"):
        if path.is_file():
            path.unlink()
    for file_path in sorted(source_dir.glob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        shutil.copy2(file_path, destination_dir / file_path.name)


def _build_tune_presets(args) -> List[TunePreset]:
    base_output_cap = args.ai_max_output_tokens or 1600
    return [
        TunePreset(name="cost-first", max_sources=6, preview_chars=700, max_output_tokens=max(700, base_output_cap - 500)),
        TunePreset(name="lean-balanced", max_sources=8, preview_chars=900, max_output_tokens=max(900, base_output_cap - 300)),
        TunePreset(name="balanced", max_sources=10, preview_chars=1100, max_output_tokens=base_output_cap),
        TunePreset(name="quality-lean", max_sources=12, preview_chars=1400, max_output_tokens=base_output_cap + 300),
    ]


def _candidate_sort_key(item: TuneRunResult) -> tuple[float, float, int]:
    return (
        item.estimated_cost,
        -item.quality_score,
        int(item.token_usage.get("total_tokens", 0) or 0),
    )


def _write_tune_report(
    *,
    output_root: Path,
    runs: List[TuneRunResult],
    best: TuneRunResult,
    threshold: float,
) -> Path:
    max_quality = max(run.quality_score for run in runs) if runs else 0.0
    qualified_runs = [
        run for run in runs if (max_quality <= 0.0 or run.quality_score >= (max_quality * threshold))
    ]

    lines = [
        "# Token Optimization Report",
        "",
        "Auto-tune benchmark completed with quality-and-cost scoring.",
        "",
        f"Quality threshold factor: {threshold:.2f}",
        "",
        "| Preset | Max Sources | Preview Chars | Max Output Tokens | Prompt Tokens | Completion Tokens | Total Tokens | Estimated Cost | Quality Score | Qualified | Output Folder |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    qualified_names = {run.preset.name for run in qualified_runs}
    for run in runs:
        usage = run.token_usage
        lines.append(
            f"| {run.preset.name} | {run.preset.max_sources} | {run.preset.preview_chars} | "
            f"{run.preset.max_output_tokens} | {usage.get('prompt_tokens', 0)} | "
            f"{usage.get('completion_tokens', 0)} | {usage.get('total_tokens', 0)} | "
            f"${run.estimated_cost:.6f} | {run.quality_score:.3f} | "
            f"{'yes' if run.preset.name in qualified_names else 'no'} | {run.output_dir.name} |"
        )

    lines.extend(
        [
            "",
            "## Recommended Settings",
            "",
            f"- Preset: {best.preset.name}",
            f"- --token-max-sources {best.preset.max_sources}",
            f"- --token-preview-chars {best.preset.preview_chars}",
            f"- --ai-max-output-tokens {best.preset.max_output_tokens}",
            "",
            "Environment equivalent:",
            "",
            "```dotenv",
            f"AGENTIC_CONTEXT_MAX_SOURCES={best.preset.max_sources}",
            f"AGENTIC_CONTEXT_PREVIEW_CHARS={best.preset.preview_chars}",
            f"AGENTIC_AI_MAX_OUTPUT_TOKENS={best.preset.max_output_tokens}",
            "```",
            "",
            "Selected outputs were copied into the main output folder.",
        ]
    )

    report_path = output_root / "token-optimization-report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def _run_token_auto_tune(
    *,
    args,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    system_intent_path: str,
) -> int:
    if args.demo_mode:
        raise ValueError("--auto-tune-tokens cannot be combined with --demo-mode")
    if args.compare_with_claude:
        raise ValueError("--auto-tune-tokens currently supports single-model runs only")
    if args.dry_run:
        raise ValueError("--auto-tune-tokens requires live AI generation, not --dry-run")
    if not args.use_ai:
        raise ValueError("--auto-tune-tokens requires --use-ai")

    from llm.factory import build_llm_client, load_llm_settings
    from orchestrator.pipeline import PipelineRunner

    threshold = min(1.0, max(0.0, float(args.auto_tune_quality_threshold)))
    presets = _build_tune_presets(args)
    run_results: List[TuneRunResult] = []

    print(f"[AUTO-TUNE] Evaluating {len(presets)} token presets...")

    for index, preset in enumerate(presets, start=1):
        os.environ["AGENTIC_CONTEXT_MAX_SOURCES"] = str(preset.max_sources)
        os.environ["AGENTIC_CONTEXT_PREVIEW_CHARS"] = str(preset.preview_chars)
        os.environ["AGENTIC_AI_MAX_OUTPUT_TOKENS"] = str(preset.max_output_tokens)

        llm_settings = load_llm_settings()
        llm_client = build_llm_client(llm_settings)
        if llm_client is None:
            raise ValueError("Failed to initialize LLM client for token auto-tune run")

        candidate_dir = output_root.parent / f"{output_root.name}_autotune_{index}_{_sanitize_name(preset.name)}"
        if candidate_dir.exists():
            shutil.rmtree(candidate_dir)

        print(
            "[AUTO-TUNE] "
            f"{index}/{len(presets)} {preset.name} "
            f"(sources={preset.max_sources}, preview={preset.preview_chars}, output={preset.max_output_tokens})"
        )

        runner = PipelineRunner(
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            output_root=candidate_dir,
            dry_run=False,
            llm_client=llm_client,
            extra_context={"system_intent_path": system_intent_path},
        )
        results = runner.run()
        usage = _sum_token_usage(results)
        estimated_cost = _estimate_primary_cost(usage)
        quality_score = _score_artifact_quality(candidate_dir)
        run_results.append(
            TuneRunResult(
                preset=preset,
                output_dir=candidate_dir,
                token_usage=usage,
                estimated_cost=estimated_cost,
                quality_score=quality_score,
            )
        )

    if not run_results:
        raise RuntimeError("Token auto-tune did not produce any candidate runs")

    max_quality = max(item.quality_score for item in run_results)
    qualified = [
        item
        for item in run_results
        if max_quality <= 0.0 or item.quality_score >= (max_quality * threshold)
    ]
    if not qualified:
        qualified = run_results

    best = min(qualified, key=_candidate_sort_key)

    _copy_selected_artifacts(best.output_dir, output_root)
    report_path = _write_tune_report(
        output_root=output_root,
        runs=run_results,
        best=best,
        threshold=threshold,
    )

    print("[AUTO-TUNE] Completed.")
    print(f"[AUTO-TUNE] Recommended preset: {best.preset.name}")
    print(
        "[AUTO-TUNE] Recommended flags: "
        f"--token-max-sources {best.preset.max_sources} "
        f"--token-preview-chars {best.preset.preview_chars} "
        f"--ai-max-output-tokens {best.preset.max_output_tokens}"
    )
    print(f"[AUTO-TUNE] Best output copied to: {output_root}")
    print(f"[AUTO-TUNE] Report written: {report_path}")
    return 0


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    framework_root = repo_root / ".agentic-sdlc"
    sys.path.insert(0, str(framework_root))
    load_local_dotenv(repo_root)

    from orchestrator.config import load_pipeline_config
    from llm.factory import build_llm_client, load_llm_settings

    pipeline_path = framework_root / "pipelines" / f"{args.pipeline}.yaml"
    templates_dir = framework_root / "templates"

    requested_input = (repo_root / args.input).resolve()
    requested_output = (repo_root / args.output).resolve()

    input_root = requested_input
    if not input_root.exists():
        input_root = (framework_root / args.input).resolve()
    output_root = requested_output
    if not output_root.parent.exists():
        output_root = (framework_root / args.output).resolve()

    system_intent_path = resolve_system_intent_path(args, repo_root, framework_root)

    pipeline = load_pipeline_config(pipeline_path)

    apply_ai_env_overrides(args)
    apply_token_optimization_overrides(args)

    if args.auto_tune_tokens:
        return _run_token_auto_tune(
            args=args,
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            output_root=output_root,
            system_intent_path=system_intent_path,
        )

    llm_settings = load_llm_settings()
    llm_client = build_llm_client(llm_settings)

    compare_enabled = args.compare_with_claude or args.demo_mode

    if compare_enabled:
        return _run_dual_model(
            args=args,
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            output_root=output_root,
            llm_settings=llm_settings,
            llm_client=llm_client,
            system_intent_path=system_intent_path,
        )

    return _run_single_model(
        args=args,
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        llm_settings=llm_settings,
        llm_client=llm_client,
        system_intent_path=system_intent_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
