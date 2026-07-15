from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local Agentic SDLC pipelines for spec-driven development and modernization."
    )
    parser.add_argument(
        "--pipeline",
        required=True,
        help="Pipeline name (without extension), for example mainframe_modernization.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input folder containing legacy source and context documents.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output folder where generated artifacts are written.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate placeholder artifacts without claiming implementation-ready content.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    framework_root = repo_root / ".agentic-sdlc"
    sys.path.insert(0, str(framework_root))

    from orchestrator.config import load_pipeline_config
    from orchestrator.pipeline import PipelineRunner

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
    runner = PipelineRunner(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        dry_run=args.dry_run,
    )

    results = runner.run()
    print(f"Pipeline: {pipeline.name}")
    print(f"Description: {pipeline.description}")
    print(f"Dry run: {args.dry_run}")
    for result in results:
        outputs = ", ".join(path.name for path in result.outputs)
        print(f"- {result.agent_name}: {outputs}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
