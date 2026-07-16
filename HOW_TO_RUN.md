# How to Run

## 0. Fastest Way (Recommended)

Use the helper launcher from repository root:

```powershell
# Edit .env once and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

This command now installs required Python packages automatically on both Windows and macOS before running the pipeline.

If you prefer passing the key inline instead of .env:

```powershell
python run.py --mode openai --openai-api-key <YOUR_KEY>
```

Recommended OpenAI flow:

```powershell
# Edit .env once and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

You can override folders if needed:

```powershell
python run.py --mode openai --openai-api-key <YOUR_KEY> --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output
```

## 1. Prerequisites

- Python 3.11+ installed
- VS Code with GitHub Copilot enabled

## 2. Install Dependencies

Optional (manual install if you do not want auto-install in `run.py`):

```powershell
python -m pip install -r requirements.txt
```

To skip auto-install in the runner:

```powershell
python run.py --no-install --mode openai --openai-api-key <YOUR_KEY>
```

## 3. Prepare Input Files

Put legacy files in:

- `.agentic-sdlc/examples/inqacc/legacy/cobol`
- `.agentic-sdlc/examples/inqacc/legacy/copybooks`

## 4. Run Mainframe Modernization Pipeline

OpenAI-first command:

```powershell
# Edit .env once and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

Console output order:

1. Input root and detected input files
2. Agent execution plan
3. Per-agent progress (`[START]` / `[DONE]`) with generated output files

Equivalent explicit command with pipeline/input/output paths:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

## 5. Run in Dry-Run Mode

```powershell
python run_pipeline.py --dry-run
```

## 6. Run with Actual AI (Optional)

### OpenAI-Compatible Endpoint (Primary)

```powershell
python run_pipeline.py --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

The repository includes a committed `.env` with safe defaults. After pulling, add only your key in `AGENTIC_AI_API_KEY`.

### Optional: Local Ollama (Fallback)

Use this only if you want local model execution instead of OpenAI:

```powershell
python run_pipeline.py --use-ai --ai-provider ollama --ai-model llama3.1 --ai-base-url http://localhost:11434
```

## 7. Expected Output Artifacts

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

## 8. Validate with Tests

```powershell
python -m pytest -q tests
```

## 9. Use Outputs with Copilot

1. Open generated artifacts in VS Code.
2. Start from `spec.md` as source of truth.
3. Use `copilot-build-prompt.md` to drive incremental implementation.
4. Validate coverage with `mapping-matrix.md`, `traceability-matrix.md`, and `test-spec.md`.

## 10. Troubleshooting

- If `pytest` is missing:

```powershell
python -m pip install pytest PyYAML
```

- If pipeline file is not found, check pipeline name under `.agentic-sdlc/pipelines`.
- If no outputs are generated, verify `--input` path has COBOL/copybook files.
- If AI mode fails with connection errors, verify `--ai-base-url` and provider availability.
