# How To Run

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

## Run Dual-Model Comparison (Primary + Claude)

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <PRIMARY_KEY> --compare-with-claude --claude-model claude-haiku-4-5-20251001 --claude-api-key <CLAUDE_KEY>
```

Dual-run requirements:

- Primary key required: `AGENTIC_AI_API_KEY`
- Claude key required: `AGENTIC_CLAUDE_API_KEY`

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
