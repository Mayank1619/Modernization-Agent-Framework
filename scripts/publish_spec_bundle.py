from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a local Spec Kit bundle into a target project folder."
    )
    parser.add_argument(
        "--bundle-dir",
        default=".agentic-sdlc/spec-kit-bundles/current",
        help="Local bundle directory created by build_spec_bundle.py",
    )
    parser.add_argument(
        "--target-project-dir",
        default=os.getenv("SPEC_KIT_PROJECT_DIR", ""),
        help="Destination Spec Kit project root (or set SPEC_KIT_PROJECT_DIR)",
    )
    parser.add_argument(
        "--target-subdir",
        default=os.getenv("SPEC_KIT_IMPORT_SUBDIR", "spec-kit/imports"),
        help="Relative import path inside target project",
    )
    parser.add_argument(
        "--stamp",
        action="store_true",
        help="Publish into a timestamped folder under target-subdir",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    target_project_dir = Path(args.target_project_dir).resolve() if args.target_project_dir else None

    if not bundle_dir.exists() or not bundle_dir.is_dir():
        raise FileNotFoundError(f"Bundle folder not found: {bundle_dir}")
    if target_project_dir is None:
        raise ValueError("Target project dir not provided. Use --target-project-dir or SPEC_KIT_PROJECT_DIR.")
    if not target_project_dir.exists() or not target_project_dir.is_dir():
        raise FileNotFoundError(f"Target project folder not found: {target_project_dir}")

    publish_root = target_project_dir / args.target_subdir
    if args.stamp:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        publish_root = publish_root / stamp

    publish_root.mkdir(parents=True, exist_ok=True)

    for src in bundle_dir.glob("*"):
        dst = publish_root / src.name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"[SPEC-KIT] Bundle published to: {publish_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
