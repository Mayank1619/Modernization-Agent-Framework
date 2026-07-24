from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_ARTIFACTS = [
    "business-rules.md",
    "requirements.md",
    "spec.md",
    "tasks.md",
    "test-spec.md",
    "openapi.yaml",
]

ID_PATTERN = re.compile(r"\b(?:FR|BR|NFR|AC|TC|TASK)-\d+\b", re.IGNORECASE)


@dataclass
class ArtifactMetrics:
    chars: int
    headings: int
    table_rows: int
    ids: int


@dataclass
class ValidationThresholds:
    min_char_ratio: float
    max_char_ratio: float
    min_heading_ratio: float
    max_heading_ratio: float
    min_id_ratio: float
    max_id_ratio: float


@dataclass
class ArtifactValidationResult:
    artifact: str
    status: str
    reasons: List[str]
    baseline: ArtifactMetrics
    generated: ArtifactMetrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate generated artifact detail level against Spec Kit baseline to "
            "detect under-specification and over-specification drift."
        )
    )
    parser.add_argument(
        "--generated-output",
        default=".agentic-sdlc/examples/inqacc/output",
        help="Generated artifact folder to validate.",
    )
    parser.add_argument(
        "--bundle-specs",
        default=".agentic-sdlc/spec-kit-bundles/current/specs",
        help="Spec Kit specs folder used as baseline.",
    )
    parser.add_argument(
        "--artifacts",
        default=",".join(DEFAULT_ARTIFACTS),
        help="Comma-separated list of artifacts to validate.",
    )
    parser.add_argument("--min-char-ratio", type=float, default=0.75)
    parser.add_argument("--max-char-ratio", type=float, default=1.35)
    parser.add_argument("--min-heading-ratio", type=float, default=0.70)
    parser.add_argument("--max-heading-ratio", type=float, default=1.60)
    parser.add_argument("--min-id-ratio", type=float, default=0.70)
    parser.add_argument("--max-id-ratio", type=float, default=1.60)
    parser.add_argument(
        "--report-file",
        default="detail-drift-report.md",
        help="Report filename written under generated output folder.",
    )
    return parser.parse_args()


def _safe_ratio(value: int, baseline: int) -> float | None:
    if baseline <= 0:
        return None
    return value / baseline


def _ratio_text(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _metric_status(
    *,
    name: str,
    ratio: float | None,
    min_ratio: float,
    max_ratio: float,
) -> Tuple[bool, str | None]:
    if ratio is None:
        return True, None
    if ratio < min_ratio:
        return False, f"{name} ratio too low ({ratio:.2f} < {min_ratio:.2f})"
    if ratio > max_ratio:
        return False, f"{name} ratio too high ({ratio:.2f} > {max_ratio:.2f})"
    return True, None


def collect_metrics(path: Path) -> ArtifactMetrics:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    return ArtifactMetrics(
        chars=len(text),
        headings=sum(1 for line in lines if line.lstrip().startswith("#")),
        table_rows=sum(1 for line in lines if "|" in line),
        ids=len(ID_PATTERN.findall(text)),
    )


def validate_artifact(
    *,
    artifact: str,
    baseline_dir: Path,
    generated_dir: Path,
    thresholds: ValidationThresholds,
) -> ArtifactValidationResult:
    baseline_path = baseline_dir / artifact
    generated_path = generated_dir / artifact

    if not baseline_path.exists() or not baseline_path.is_file():
        return ArtifactValidationResult(
            artifact=artifact,
            status="warn",
            reasons=["Baseline artifact is missing, skipped."],
            baseline=ArtifactMetrics(0, 0, 0, 0),
            generated=ArtifactMetrics(0, 0, 0, 0),
        )

    if not generated_path.exists() or not generated_path.is_file():
        baseline = collect_metrics(baseline_path)
        return ArtifactValidationResult(
            artifact=artifact,
            status="fail",
            reasons=["Generated artifact is missing."],
            baseline=baseline,
            generated=ArtifactMetrics(0, 0, 0, 0),
        )

    baseline = collect_metrics(baseline_path)
    generated = collect_metrics(generated_path)

    char_ratio = _safe_ratio(generated.chars, baseline.chars)
    heading_ratio = _safe_ratio(generated.headings, baseline.headings)
    id_ratio = _safe_ratio(generated.ids, baseline.ids)

    reasons: List[str] = []

    checks = [
        _metric_status(
            name="chars",
            ratio=char_ratio,
            min_ratio=thresholds.min_char_ratio,
            max_ratio=thresholds.max_char_ratio,
        ),
        _metric_status(
            name="headings",
            ratio=heading_ratio,
            min_ratio=thresholds.min_heading_ratio,
            max_ratio=thresholds.max_heading_ratio,
        ),
        _metric_status(
            name="ids",
            ratio=id_ratio,
            min_ratio=thresholds.min_id_ratio,
            max_ratio=thresholds.max_id_ratio,
        ),
    ]

    for passed, message in checks:
        if not passed and message:
            reasons.append(message)

    status = "pass" if not reasons else "fail"
    if baseline.headings == 0 and baseline.ids == 0:
        # For low-structure artifacts (often YAML), only char ratio is meaningful.
        status = "pass" if len(reasons) <= 0 else "fail"

    return ArtifactValidationResult(
        artifact=artifact,
        status=status,
        reasons=reasons,
        baseline=baseline,
        generated=generated,
    )


def build_report(
    *,
    results: List[ArtifactValidationResult],
    thresholds: ValidationThresholds,
) -> str:
    fails = [item for item in results if item.status == "fail"]
    warns = [item for item in results if item.status == "warn"]

    lines = [
        "# Detail Drift Validation Report",
        "",
        "Compares generated artifacts against the Spec Kit baseline to catch under- and over-detail drift.",
        "",
        "## Thresholds",
        "",
        f"- Char ratio: {thresholds.min_char_ratio:.2f} to {thresholds.max_char_ratio:.2f}",
        f"- Heading ratio: {thresholds.min_heading_ratio:.2f} to {thresholds.max_heading_ratio:.2f}",
        f"- ID ratio: {thresholds.min_id_ratio:.2f} to {thresholds.max_id_ratio:.2f}",
        "",
        f"## Summary\n\n- Pass: {len(results) - len(fails) - len(warns)}\n- Warn: {len(warns)}\n- Fail: {len(fails)}",
        "",
        "## Results",
        "",
        "| Artifact | Status | Baseline chars | Generated chars | Char ratio | Heading ratio | ID ratio | Notes |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]

    for item in results:
        char_ratio = _ratio_text(_safe_ratio(item.generated.chars, item.baseline.chars))
        heading_ratio = _ratio_text(_safe_ratio(item.generated.headings, item.baseline.headings))
        id_ratio = _ratio_text(_safe_ratio(item.generated.ids, item.baseline.ids))
        notes = "; ".join(item.reasons) if item.reasons else "within thresholds"
        lines.append(
            f"| {item.artifact} | {item.status} | {item.baseline.chars} | {item.generated.chars} | "
            f"{char_ratio} | {heading_ratio} | {id_ratio} | {notes} |"
        )

    lines.append("")
    if fails:
        lines.append("Validation failed because at least one artifact drifted outside configured thresholds.")
    else:
        lines.append("Validation passed.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    generated_dir = Path(args.generated_output).resolve()
    baseline_dir = Path(args.bundle_specs).resolve()
    artifacts = [name.strip() for name in args.artifacts.split(",") if name.strip()]

    if not generated_dir.exists() or not generated_dir.is_dir():
        raise FileNotFoundError(f"Generated output folder not found: {generated_dir}")
    if not baseline_dir.exists() or not baseline_dir.is_dir():
        raise FileNotFoundError(f"Bundle specs folder not found: {baseline_dir}")

    thresholds = ValidationThresholds(
        min_char_ratio=args.min_char_ratio,
        max_char_ratio=args.max_char_ratio,
        min_heading_ratio=args.min_heading_ratio,
        max_heading_ratio=args.max_heading_ratio,
        min_id_ratio=args.min_id_ratio,
        max_id_ratio=args.max_id_ratio,
    )

    results = [
        validate_artifact(
            artifact=artifact,
            baseline_dir=baseline_dir,
            generated_dir=generated_dir,
            thresholds=thresholds,
        )
        for artifact in artifacts
    ]

    report = build_report(results=results, thresholds=thresholds)
    report_path = generated_dir / args.report_file
    report_path.write_text(report, encoding="utf-8")

    fail_count = sum(1 for item in results if item.status == "fail")
    warn_count = sum(1 for item in results if item.status == "warn")
    print(f"[DETAIL-DRIFT] Report: {report_path}")
    print(f"[DETAIL-DRIFT] Pass={len(results) - fail_count - warn_count} Warn={warn_count} Fail={fail_count}")

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
