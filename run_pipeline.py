from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


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
        choices=["ollama", "openai"],
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
    parser.epilog = (
        "Examples:\n"
        "  python run_pipeline.py\n"
        "  python run_pipeline.py --dry-run\n"
        "  python run_pipeline.py --use-ai --ai-provider ollama --ai-model llama3.1 "
        "--ai-base-url http://localhost:11434\n"
        "  python run_pipeline.py --use-ai --ai-provider openai --ai-model gpt-4o-mini "
        "--ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    framework_root = repo_root / ".agentic-sdlc"
    sys.path.insert(0, str(framework_root))
    load_local_dotenv(repo_root)

    from orchestrator.config import load_pipeline_config
    from orchestrator.pipeline import PipelineRunner
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

    pipeline = load_pipeline_config(pipeline_path)

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

    llm_settings = load_llm_settings()
    llm_client = build_llm_client(llm_settings)

    runner = PipelineRunner(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        dry_run=args.dry_run,
        llm_client=llm_client,
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
