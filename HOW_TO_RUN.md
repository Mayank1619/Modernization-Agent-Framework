# How to Run

## 0. Fastest Way (Recommended)

```powershell
# Edit .env and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

## 1. Prerequisites

- Python 3.11+
- VS Code with GitHub Copilot

## 2. Install Dependencies

Optional if using run.py auto-install:

```powershell
python -m pip install -r requirements.txt
```

## 3. Prepare Input Files

- .agentic-sdlc/examples/inqacc/legacy/cobol
- .agentic-sdlc/examples/inqacc/legacy/copybooks

## 4. Mainframe Pipeline (OpenAI)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

Optional system intent input:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

## 5. Dry Run

```powershell
python run_pipeline.py --dry-run
```

## 6. Dual-Model Verification (OpenAI + Claude)

Verify Claude first:

```powershell
python test_claude_api.py
```

Run dual-model compare + merge:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <PRIMARY_KEY> --compare-with-claude --claude-model claude-haiku-4-5-20251001 --claude-api-key <CLAUDE_KEY>
```

Generated folders/files in dual mode:

- .agentic-sdlc/examples/inqacc/output_primary
- .agentic-sdlc/examples/inqacc/output_claude
- .agentic-sdlc/examples/inqacc/output
- .agentic-sdlc/examples/inqacc/output/dual-model-analysis.md

## 7. Expected Artifacts

- program-analysis.md
- business-rules.md
- intended-system.md
- requirements.md
- spec.md
- plan.md
- tasks.md
- mapping-matrix.md
- traceability-matrix.md
- test-spec.md
- openapi.yaml
- copilot-build-prompt.md
- qa-review-checklist.md
- code-review-checklist.md
- modernization-report.md
- dual-model-analysis.md (dual mode)

## 8. Tests

```powershell
python -m pytest -q tests
```
