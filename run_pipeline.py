from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple


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
    parser.epilog = (
        "Examples:\n"
        "  python run_pipeline.py\n"
        "  python run_pipeline.py --dry-run\n"
        "  python run_pipeline.py --use-ai --ai-provider ollama --ai-model llama3.1 "
        "--ai-base-url http://localhost:11434\n"
        "  python run_pipeline.py --use-ai --ai-provider openai --ai-model gpt-4o-mini "
        "--ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>\n"
        "  python run_pipeline.py --use-ai --ai-provider openai --compare-with-claude "
        "--claude-model claude-haiku-4-5-20251001"
    )
    return parser.parse_args()


def build_claude_settings(args) -> Tuple[str, str, str]:
    model = (
        args.claude_model
        or os.getenv("AGENTIC_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    ).strip()
    base_url = (args.claude_base_url or os.getenv(
        "AGENTIC_CLAUDE_BASE_URL", "https://api.anthropic.com"
    )).strip()
    api_key = (args.claude_api_key or os.getenv("AGENTIC_CLAUDE_API_KEY", "")).strip()
    if not api_key:
        raise ValueError(
            "Claude dual-run requires a key. Set --claude-api-key or AGENTIC_CLAUDE_API_KEY."
        )
    return model, base_url, api_key


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
        claude_model, claude_base_url, claude_api_key = build_claude_settings(args)
        claude_client = build_llm_client(
            LlmSettings(
                enabled=True,
                provider="claude",
                model=claude_model,
                base_url=claude_base_url,
                api_key=claude_api_key,
                timeout_seconds=llm_settings.timeout_seconds,
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
        extra_context={"system_intent_path": system_intent_path},
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
