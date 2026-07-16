from __future__ import annotations

import argparse
import os
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="User-friendly launcher for the mainframe modernization pipeline."
    )
    parser.add_argument(
        "--mode",
        choices=["template", "dry-run", "ollama", "openai"],
        default="template",
        help="Run mode. Default: template.",
    )
    parser.add_argument(
        "--input",
        default=".agentic-sdlc/examples/inqacc/legacy",
        help="Input folder. Default: .agentic-sdlc/examples/inqacc/legacy",
    )
    parser.add_argument(
        "--output",
        default=".agentic-sdlc/examples/inqacc/output",
        help="Output folder. Default: .agentic-sdlc/examples/inqacc/output",
    )
    parser.add_argument(
        "--openai-model",
        default="gpt-4o-mini",
        help="Model to use for openai mode. Default: gpt-4o-mini",
    )
    parser.add_argument(
        "--openai-base-url",
        default="https://api.openai.com",
        help="Base URL to use for openai mode.",
    )
    parser.add_argument(
        "--openai-api-key",
        default="",
        help="API key for openai mode. Can be omitted if AGENTIC_AI_API_KEY is set.",
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.1",
        help="Model to use for ollama mode. Default: llama3.1",
    )
    parser.add_argument(
        "--ollama-base-url",
        default="http://localhost:11434",
        help="Base URL to use for ollama mode.",
    )
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    cmd = [
        sys.executable,
        "run_pipeline.py",
        "--pipeline",
        "mainframe_modernization",
        "--input",
        args.input,
        "--output",
        args.output,
    ]

    if args.mode == "dry-run":
        cmd.append("--dry-run")
    elif args.mode == "ollama":
        cmd.extend(
            [
                "--use-ai",
                "--ai-provider",
                "ollama",
                "--ai-model",
                args.ollama_model,
                "--ai-base-url",
                args.ollama_base_url,
            ]
        )
    elif args.mode == "openai":
        api_key = args.openai_api_key or os.getenv("AGENTIC_AI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "OpenAI API key missing. Pass --openai-api-key or set AGENTIC_AI_API_KEY."
            )

        cmd.extend(
            [
                "--use-ai",
                "--ai-provider",
                "openai",
                "--ai-model",
                args.openai_model,
                "--ai-base-url",
                args.openai_base_url,
                "--ai-api-key",
                api_key,
            ]
        )

    return cmd


def main() -> int:
    args = parse_args()
    cmd = build_command(args)

    print("== Agentic SDLC Runner ==")
    print(f"Mode: {args.mode}")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print("Running command:")
    print(" ".join(cmd))

    completed = subprocess.run(cmd, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
