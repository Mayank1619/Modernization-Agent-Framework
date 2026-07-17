from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple


def load_local_dotenv(repo_root: Path) -> None:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


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
    if args.use_ai:
        os.environ["AGENTIC_AI_ENABLED"] = "true"
    if args.ai_provider:
        os.environ["AGENTIC_AI_PROVIDER"] = args.ai_provider
    if args.ai_model:
        os.environ["AGENTIC_AI_MODEL"] = args.ai_model
    if args.ai_base_url:
        os.environ["AGENTIC_AI_BASE_URL"] = args.ai_base_url
    if args.ai_api_key:
        os.environ["AGENTIC_AI_API_KEY"] = args.ai_api_key


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    framework_root = repo_root / ".agentic-sdlc"
    sys.path.insert(0, str(framework_root))
    load_local_dotenv(repo_root)

    from orchestrator.config import load_pipeline_config
    from orchestrator.dual_run import run_pipeline_dual_model
    from orchestrator.pipeline import PipelineRunner
    from llm.factory import LlmSettings, build_llm_client, load_llm_settings

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

    llm_settings = load_llm_settings()
    llm_client = build_llm_client(llm_settings)

    if args.compare_with_claude:
        if args.dry_run:
            raise ValueError("--compare-with-claude cannot be combined with --dry-run")
        if not llm_settings.enabled or llm_client is None:
            raise ValueError(
                "Dual-model comparison requires primary AI generation. "
                "Use --use-ai with a primary provider."
            )

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

        comparisons = run_pipeline_dual_model(
            pipeline=pipeline,
            templates_dir=templates_dir,
            input_root=input_root,
            output_root=output_root,
            primary_client=llm_client,
            secondary_client=claude_client,
            extra_context={"system_intent_path": system_intent_path},
        )

        print(f"Pipeline: {pipeline.name}")
        print(f"Description: {pipeline.description}")
        print("Dual-model comparison: enabled")
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


if __name__ == "__main__":
    raise SystemExit(main())
