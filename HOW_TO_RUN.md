# How to Run

## 0. Fastest Way (Recommended)

```powershell
# Keep .env key-safe (blank keys), put real keys in .env.local
python run.py --mode openai
```

## 0.1 Environment Files (Push-Safe)

Use this precedence order:

1. Process environment variables (highest)
2. `.env.local` (local secrets, git-ignored)
3. `.env` (committed defaults, no secrets)

Rules:

- Keep `AGENTIC_AI_API_KEY=` blank in `.env` before commit/push.
- Keep `AGENTIC_CLAUDE_API_KEY=` blank in `.env` before commit/push.
- Put real keys only in `.env.local`.

Suggested `.env.local` content:

```dotenv
AGENTIC_AI_API_KEY=<YOUR_OPENAI_KEY>
AGENTIC_CLAUDE_API_KEY=<YOUR_CLAUDE_KEY>
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

Requirements for dual-model mode:

- `AGENTIC_AI_API_KEY` must be set (primary OpenAI-compatible run).
- `AGENTIC_CLAUDE_API_KEY` must be set (secondary Claude run).
- If either key is missing, the run fails fast with an explicit error.

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

## 9. Visual Agent Dashboard (React + API)

Start API backend in one terminal:

```powershell
python -m uvicorn agent_visual_api:app --reload --port 8000
```

Start React UI in another terminal:

```powershell
cd agent-visual-ui
npm install
npm run dev
```

Open `http://localhost:5173`.

From the UI you can:

- Start pipeline runs
- Watch agent start/completion events in near real time
- Inspect generated artifacts in the built-in viewer

AI mode behavior in UI:

- `Use AI = off` works without any keys (dry-run behavior).
- `Use AI = on` requires `AGENTIC_AI_API_KEY`.
- `Compare with Claude = on` additionally requires `AGENTIC_CLAUDE_API_KEY`.
