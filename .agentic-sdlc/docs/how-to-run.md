# How To Run

## Execution Paths

- Deterministic pipeline (`--dry-run`): no API keys required.
- Single-model AI pipeline (`--use-ai`): primary provider key required.
- Dual-model pipeline (`--compare-with-claude`): primary + Claude keys required.
- Demo dual-model pipeline (`--demo-mode`): non-AI primary/claude/merge phases.

## Environment Setup (Safe Commit Workflow)

Load order:

1. Process environment variables
2. `.env.local` (local secrets, git-ignored)
3. `.env` (committed defaults, no secrets)

Requirements:

- Keep `AGENTIC_AI_API_KEY=` blank in committed `.env`.
- Keep `AGENTIC_CLAUDE_API_KEY=` blank in committed `.env`.
- Put real keys in `.env.local` only.

Example `.env.local`:

```dotenv
AGENTIC_AI_API_KEY=<YOUR_OPENAI_KEY>
AGENTIC_CLAUDE_API_KEY=<YOUR_CLAUDE_KEY>
```

## Run Mainframe Modernization Pipeline

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output
```

Deterministic mode:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --dry-run
```

Single-model AI mode:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com
```

## Run Dual-Model Comparison (Primary + Claude)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <PRIMARY_KEY> --compare-with-claude --claude-model claude-haiku-4-5-20251001 --claude-api-key <CLAUDE_KEY>
```

Dual-run requirements:

- Primary key required: `AGENTIC_AI_API_KEY`
- Claude key required: `AGENTIC_CLAUDE_API_KEY`

Performance controls:

- `--parallel-dual-run` (default on)
- `--no-parallel-dual-run`
- `--optimize-tokens`
- `--token-max-sources`
- `--token-preview-chars`

Demo dual flow:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --demo-mode --parallel-dual-run
```

## Verify Claude API Before Dual Run

```powershell
python test_claude_api.py
```

Optional with explicit target-system constraints:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md
```

## Run Dry-Run Mode

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --dry-run
```

Dry-run note:

- Dry-run works without keys when AI is disabled.

## Visual API + Dashboard Flow

Fastest start (Windows PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dashboard.ps1
```

Optional custom ports:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dashboard.ps1 -ApiPort 8010 -UiPort 5175
```

Manual start:

Start backend:

```powershell
python -m uvicorn agent_visual_api:app --reload --port 8000
```

Start frontend:

```powershell
cd agent-visual-ui
npm install
npm run dev
```

Open `http://localhost:5173`.

Behavior:

- `Use OpenAI = off` runs deterministic mode.
- `Use OpenAI = on` requires `AGENTIC_AI_API_KEY`.
- `Use Claude = on` requires `AGENTIC_CLAUDE_API_KEY`.
- `Demo Mode = on` runs full dual phases without keys.
- `Run OpenAI + Claude in Parallel` controls concurrent dual execution.
- `Optimize Token Usage` applies compact prompt context limits.
- Elapsed timer shows current run duration.
- Dual runs emit phase events and merge summary in run events.
- Dual execution map shows both model flows converging to `Merge + Compare`, then `Final Output`.
- Run controls display resolved OpenAI and Claude model names.

## Expected Outputs

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
- dual-model-analysis.md (when --compare-with-claude is used)
