# Copilot Custom Agents (Workspace)

This repo now includes workspace custom agents under `.github/agents/`.

## Available Agents

- `SpecKit Orchestrator`
- `Legacy Analysis Specialist`
- `Business Rules Specialist`
- `Requirements and Spec Specialist`
- `Contract and Mapping Specialist`
- `Plan and Tasks Specialist`
- `Test and Review Specialist`
- `Quality Gates Specialist`

## How to Use in VS Code Copilot

1. Open Copilot Chat.
2. Switch to Agent mode.
3. Pick `SpecKit Orchestrator` from the agent picker.
4. Give one input prompt with scope, for example:

```text
Generate modernization artifacts for INQACC account inquiry.
Use legacy assets from .agentic-sdlc/examples/inqacc/legacy.
Write outputs to .agentic-sdlc/examples/inqacc/output.
Run quality gates and return readiness summary.
```

The orchestrator delegates internally to specialist agents.

## Quality Gate Commands

Use these in `Quality Gates Specialist` when needed:

- `python -m pytest -q tests`
- `python scripts/validate_detail_drift.py --generated-output .agentic-sdlc/examples/inqacc/output --bundle-specs .agentic-sdlc/spec-kit-bundles/current/specs`

## Notes

- Specialist agents are `user-invocable: false` and designed for orchestrated delegation.
- If you prefer direct selection of specialists, set `user-invocable: true` in each agent file.
