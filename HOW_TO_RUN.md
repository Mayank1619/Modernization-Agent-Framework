# How to Run

## 0. Execution Modes

- Deterministic mode: no LLM calls, fastest for scaffolding.
- Single-model AI mode: one provider run into output.
- Dual-model mode: primary + Claude compare and merge.
- Demo dual-model mode: non-AI run that still executes primary, claude, and merge phases.

## 1. Environment Files (Push-Safe)

```powershell
# Keep key values empty in .env before commit/push
# Put actual keys only in .env.local
```

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

## 2. Prerequisites

- Python 3.11+
- Node.js 18+ (for React dashboard)
- VS Code with GitHub Copilot

## 3. Install Dependencies

Optional if using run.py auto-install:

```powershell
python -m pip install -r requirements.txt
```

For dashboard UI:

```powershell
cd agent-visual-ui
npm install
```

## 4. Prepare Input Files

- .agentic-sdlc/examples/inqacc/legacy/cobol
- .agentic-sdlc/examples/inqacc/legacy/copybooks

## 5. Deterministic Run (No AI)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --dry-run
```

## 6. Single-Model AI Run (OpenAI-Compatible)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

Optional system intent input:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

## 7. Dual-Model Verification (OpenAI + Claude)

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

Parallel execution option:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --compare-with-claude --parallel-dual-run
```

Sequential fallback:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --compare-with-claude --no-parallel-dual-run
```

Token optimization options:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --optimize-tokens --token-max-sources 12 --token-preview-chars 1400
```

Auto-tune token settings (single-model AI mode):

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --auto-tune-tokens
```

Optional quality threshold override:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --auto-tune-tokens --auto-tune-quality-threshold 0.95
```

Auto-tune outputs:

- Candidate folders: `<output>_autotune_*`
- Selected best artifacts copied into configured output folder
- Report: `token-optimization-report.md`

Auto-tune constraints:

- Requires `--use-ai`
- Single-model mode only (do not combine with `--compare-with-claude`)
- Cannot be combined with `--dry-run` or `--demo-mode`

Add output token caps:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --optimize-tokens --token-max-sources 10 --token-preview-chars 1000 --ai-max-output-tokens 1600
```

Dual-run with explicit Claude cap:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --compare-with-claude --parallel-dual-run --ai-max-output-tokens 1800 --claude-max-output-tokens 1200
```

Output cap precedence:

- Primary provider: `--ai-max-output-tokens` -> `AGENTIC_AI_MAX_OUTPUT_TOKENS`
- Claude in dual mode: `--claude-max-output-tokens` -> `AGENTIC_CLAUDE_MAX_OUTPUT_TOKENS` -> `AGENTIC_AI_MAX_OUTPUT_TOKENS`

Token cost model:

- Estimated cost = `(prompt_tokens / 1000 * prompt_rate) + (completion_tokens / 1000 * completion_rate)`
- Completion tokens are typically the largest variable cost and should be tuned first.

Suggested optimization workflow:

1. Start with balanced settings: max sources 8-10, preview chars 900-1200, output cap 1400-1800.
2. Run a representative sample input set and capture token usage.
3. Reduce output cap first in 200-token steps until quality drops.
4. Reduce preview chars next in 100-200 char steps.
5. Reduce max sources last in 1-2 source steps.
6. Promote dual-run to checkpoint validation only.
7. Keep the best settings as your project baseline.

## 8. Demo Mode (Non-AI, Full Dual Flow)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --demo-mode --parallel-dual-run
```

Demo mode behavior:

- No API keys required.
- Runs primary and claude phases in dry-run mode.
- Executes merge phase and writes final output.
- Emits full phase events for realistic dashboard visualization.

## 9. Run with Visual Dashboard (API + React)

Fastest start (Windows PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dashboard.ps1
```

Optional custom ports:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dashboard.ps1 -ApiPort 8010 -UiPort 5175
```

Manual start:

Start backend API:

```powershell
python -m uvicorn agent_visual_api:app --reload --port 8000
```

Start React UI:

```powershell
cd agent-visual-ui
npm run dev
```

Open `http://localhost:5173`.

UI run behavior:

- `Use OpenAI = off` runs deterministic mode without keys.
- `Use OpenAI = on` requires `AGENTIC_AI_API_KEY`.
- `Use Claude = on` also requires `AGENTIC_CLAUDE_API_KEY`.
- `Demo Mode = on` runs full non-AI primary/claude/merge flow.
- `Run OpenAI + Claude in Parallel` controls dual-run concurrency.
- `Optimize Token Usage` enables compact prompt context.
- In dual mode, the execution map shows OpenAI/Claude flows converging to `Merge + Compare`, then `Final Output`.
- Run controls display resolved model names for OpenAI and Claude.
- Header shows elapsed run timer.
- Theme toggle switches between Classic and Neon UI.

## 10. Expected Artifacts

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

## 11. Tests

```powershell
python -m pytest -q tests
```

## 12. Fast Troubleshooting

- Error: `AGENTIC_AI_API_KEY is required for provider=openai`
	- Cause: AI mode enabled without primary key.
	- Fix: Set key in `.env.local` or pass `--ai-api-key`.

- Error: `Claude API key is required for dual-model mode`
	- Cause: compare mode enabled without Claude key.
	- Fix: Set `AGENTIC_CLAUDE_API_KEY` in `.env.local`.

- If deterministic mode is enough for demo:
	- Set `Use AI = off` in UI or use `--dry-run` in CLI.

- If dual mode is too slow:
	- Keep `--parallel-dual-run` enabled.
	- Enable `--optimize-tokens` and tune source/preview limits.
	- Set `--ai-max-output-tokens` and `--claude-max-output-tokens` to constrain completion spend.
	- Use smaller/faster models where acceptable.

