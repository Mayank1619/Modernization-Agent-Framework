from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


CANONICAL_ARTIFACTS = [
    "program-analysis.md",
    "business-rules.md",
    "intended-system.md",
    "requirements.md",
    "spec.md",
    "plan.md",
    "tasks.md",
    "mapping-matrix.md",
    "traceability-matrix.md",
    "test-spec.md",
    "openapi.yaml",
    "copilot-build-prompt.md",
    "qa-review-checklist.md",
    "code-review-checklist.md",
    "modernization-report.md",
    "dual-model-analysis.md",
    "token-optimization-report.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a normalized Spec Kit bundle from generated pipeline artifacts."
    )
    parser.add_argument(
        "--source-output",
        default=".agentic-sdlc/examples/inqacc/output",
        help="Generated artifact folder from run_pipeline.py",
    )
    parser.add_argument(
        "--bundle-dir",
        default=".agentic-sdlc/spec-kit-bundles/current",
        help="Output folder for normalized bundle",
    )
    parser.add_argument(
        "--bundle-name",
        default="mainframe-modernization-spec-bundle",
        help="Bundle name used in manifest metadata",
    )
    return parser.parse_args()


def copy_artifacts(source_output: Path, bundle_specs_dir: Path) -> list[str]:
    copied: list[str] = []
    for name in CANONICAL_ARTIFACTS:
        src = source_output / name
        if not src.exists() or not src.is_file():
            continue
        dst = bundle_specs_dir / name
        dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        copied.append(name)
    return copied


def write_manifest(bundle_dir: Path, bundle_name: str, copied: list[str], source_output: Path) -> None:
    manifest = {
        "bundle_name": bundle_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_output": source_output.as_posix(),
        "artifact_count": len(copied),
        "artifacts": copied,
        "entrypoints": {
            "spec": "specs/spec.md",
            "tasks": "specs/tasks.md",
            "tests": "specs/test-spec.md",
            "openapi": "specs/openapi.yaml",
            "implementation_prompt": "specs/copilot-build-prompt.md",
        },
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_summary(bundle_dir: Path, copied: list[str]) -> None:
    lines = [
        "# Spec Kit Bundle Summary",
        "",
        f"Artifacts copied: {len(copied)}",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- specs/{name}" for name in copied)
    lines.append("")
    lines.append("Use manifest.json for entrypoint references.")
    (bundle_dir / "bundle-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    source_output = Path(args.source_output).resolve()
    bundle_dir = Path(args.bundle_dir).resolve()
    bundle_specs_dir = bundle_dir / "specs"

    if not source_output.exists() or not source_output.is_dir():
        raise FileNotFoundError(f"Source output folder not found: {source_output}")

    bundle_specs_dir.mkdir(parents=True, exist_ok=True)

    copied = copy_artifacts(source_output, bundle_specs_dir)
    if not copied:
        raise RuntimeError(
            "No canonical artifacts were found to bundle. Generate artifacts before building a Spec Kit bundle."
        )

    write_manifest(bundle_dir, args.bundle_name, copied, source_output)
    write_summary(bundle_dir, copied)

    print(f"[SPEC-KIT] Bundle ready: {bundle_dir}")
    print(f"[SPEC-KIT] Artifacts copied: {len(copied)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
