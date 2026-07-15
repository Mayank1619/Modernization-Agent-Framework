# How to Run

## 1. Prerequisites

- Python 3.11+ installed
- VS Code with GitHub Copilot enabled

## 2. Install Dependencies

Run from the repository root:

```powershell
python -m pip install -r requirements.txt
```

## 3. Prepare Input Files

Put legacy files in:

- `.agentic-sdlc/examples/inqacc/legacy/cobol`
- `.agentic-sdlc/examples/inqacc/legacy/copybooks`

## 4. Run Mainframe Modernization Pipeline

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output
```

Alternative (also supported):

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input examples/inqacc/legacy --output examples/inqacc/output
```

## 5. Run in Dry-Run Mode

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input examples/inqacc/legacy --output examples/inqacc/output --dry-run
```

## 6. Expected Output Artifacts

After the run, output folder contains:

- `program-analysis.md`
- `business-rules.md`
- `requirements.md`
- `spec.md`
- `plan.md`
- `tasks.md`
- `mapping-matrix.md`
- `traceability-matrix.md`
- `test-spec.md`
- `openapi.yaml`
- `copilot-build-prompt.md`
- `qa-review-checklist.md`
- `code-review-checklist.md`
- `modernization-report.md`

## 7. Validate with Tests

```powershell
python -m pytest -q tests
```

## 8. Use Outputs with Copilot

1. Open generated artifacts in VS Code.
2. Start from `spec.md` as source of truth.
3. Use `copilot-build-prompt.md` to drive incremental implementation.
4. Validate coverage with `mapping-matrix.md`, `traceability-matrix.md`, and `test-spec.md`.

## 9. Troubleshooting

- If `pytest` is missing:

```powershell
python -m pip install pytest PyYAML
```

- If pipeline file is not found, check pipeline name under `.agentic-sdlc/pipelines`.
- If no outputs are generated, verify `--input` path has COBOL/copybook files.
