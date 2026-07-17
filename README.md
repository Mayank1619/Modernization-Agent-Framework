# Agentic SDLC Framework for Mainframe Modernization

This repository contains a local multi-agent framework that turns legacy assets into implementation-ready modernization artifacts with strong traceability.

## What It Generates

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

In dual-model mode it also produces:

- dual-model-analysis.md

## Core Capabilities

- Sequential multi-agent artifact generation
- System intent capture before requirements/spec generation
- Optional AI providers: Ollama, OpenAI-compatible, Claude
- Dual-model comparison and merge (primary + Claude)
- Deterministic dry-run mode

## Quick Start

Recommended runner:

```powershell
# Keep .env committed without secrets; set keys in .env.local
python run.py --mode openai
```

## Environment Configuration (Safe for Git)

The runtime loads settings in this order:

1. Process environment variables
2. `.env.local` (local secrets, git-ignored)
3. `.env` (committed defaults)

Commit policy:

- Keep `AGENTIC_AI_API_KEY=` blank in `.env`
- Keep `AGENTIC_CLAUDE_API_KEY=` blank in `.env`
- Store real keys only in `.env.local`

Example `.env.local`:

```dotenv
AGENTIC_AI_API_KEY=<YOUR_OPENAI_KEY>
AGENTIC_CLAUDE_API_KEY=<YOUR_CLAUDE_KEY>
```

Manual pipeline command:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

## Dual-Model Verification

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <PRIMARY_KEY> --compare-with-claude --claude-model claude-haiku-4-5-20251001 --claude-api-key <CLAUDE_KEY>
```

Requirements:

- Primary AI key is required for OpenAI-compatible mode.
- Claude key is required when `--compare-with-claude` is enabled.

Dual-model outputs:

- .agentic-sdlc/examples/inqacc/output_primary
- .agentic-sdlc/examples/inqacc/output_claude
- .agentic-sdlc/examples/inqacc/output
- .agentic-sdlc/examples/inqacc/output/dual-model-analysis.md

## Validate Claude Connectivity

```powershell
python test_claude_api.py
```

## Visual Layer (React)

Run API backend:

```powershell
python -m uvicorn agent_visual_api:app --reload --port 8000
```

Run React dashboard:

```powershell
cd agent-visual-ui
npm install
npm run dev
```

Then open `http://localhost:5173` to start runs, view agent execution events, and inspect generated outputs.

## Documentation

- Runbook: HOW_TO_RUN.md
- Framework docs: .agentic-sdlc/docs
- Agent catalog: AGENTS.md
