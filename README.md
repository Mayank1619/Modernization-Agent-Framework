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
# Set AGENTIC_AI_API_KEY in .env first
python run.py --mode openai
```

Manual pipeline command:

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

## Dual-Model Verification

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --system-intent .agentic-sdlc/examples/inqacc/legacy/system-intent.md --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <PRIMARY_KEY> --compare-with-claude --claude-model claude-haiku-4-5-20251001 --claude-api-key <CLAUDE_KEY>
```

Dual-model outputs:

- .agentic-sdlc/examples/inqacc/output_primary
- .agentic-sdlc/examples/inqacc/output_claude
- .agentic-sdlc/examples/inqacc/output
- .agentic-sdlc/examples/inqacc/output/dual-model-analysis.md

## Validate Claude Connectivity

```powershell
python test_claude_api.py
```

## Documentation

- Runbook: HOW_TO_RUN.md
- Framework docs: .agentic-sdlc/docs
- Agent catalog: AGENTS.md
