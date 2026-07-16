# Agentic SDLC Framework for Mainframe Modernization

This project is a local multi-agent framework that converts legacy mainframe assets and business intent into implementation-ready modernization artifacts.

It is designed for teams that want:

- A spec-driven delivery process (not ad-hoc code generation)
- Strong traceability from legacy logic to modern implementation
- AI-assisted drafting with deterministic fallback when AI is disabled
- Faster onboarding for engineering, QA, architects, and reviewers

## Why This Matters

Mainframe modernization often fails because teams jump directly into code without preserving business logic, traceability, and test intent.

This framework solves that by generating a complete artifact chain:

`Legacy Code -> Analysis -> Rules -> Requirements -> Spec -> Plan -> Tasks -> Mapping/Traceability -> Tests -> API Contract -> Copilot Prompt -> QA/Code Review -> Final Report`

## What You Get (Generated Artifacts)

Each pipeline run generates a consistent delivery packet:

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

## Tech Stack

Detailed architecture and stack notes are available in [ARCHITECTURE.md](ARCHITECTURE.md).

### Core Runtime

- Python 3.11+
- Standard library orchestration (`argparse`, `pathlib`, `dataclasses`, `urllib`)
- YAML-driven pipeline configuration

### Python Dependencies

- `PyYAML` for pipeline/template configuration parsing
- `pytest` for validation tests

### AI Integration Layer

- Provider-agnostic LLM client interface
- Local Ollama support (`/api/generate`)
- OpenAI-compatible Chat Completions support (`/v1/chat/completions`)
- Environment-variable and CLI-driven runtime configuration

### Delivery Workflow

- Multi-agent sequential pipeline orchestration
- Template-based deterministic generation (default)
- Optional live AI generation for richer outputs
- GitHub Copilot-friendly output prompts and instructions

## OpenAI API Integration

The framework includes first-class OpenAI-compatible integration.

### How It Works

- Enable AI mode with `--use-ai`
- Set provider to `openai`
- Provide model, base URL, and API key
- Framework sends a Chat Completions request and uses the response to generate artifacts

### Required Inputs for OpenAI Mode

- `--ai-provider openai`
- `--ai-model <model-name>`
- `--ai-base-url <openai-or-compatible-base-url>`
- `--ai-api-key <your-api-key>`

You can pass these via CLI flags or via environment variables:

- `AGENTIC_AI_ENABLED=true`
- `AGENTIC_AI_PROVIDER=openai`
- `AGENTIC_AI_MODEL=...`
- `AGENTIC_AI_BASE_URL=https://api.openai.com`
- `AGENTIC_AI_API_KEY=...`

### OpenAI Example Command

```powershell
python run_pipeline.py --pipeline mainframe_modernization --input examples/inqacc/legacy --output examples/inqacc/output --use-ai --ai-provider openai --ai-model gpt-4o-mini --ai-base-url https://api.openai.com --ai-api-key <YOUR_KEY>
```

If `--use-ai` is not set, the framework runs in deterministic local template mode.

## Agent Catalog (What Each Agent Does)

Pipeline: `mainframe_modernization`

1. `LegacyAnalysisAgent`
- Reads COBOL/copybook context.
- Produces: `program-analysis.md`

2. `BusinessRulesAgent`
- Extracts and clarifies business logic and constraints.
- Produces: `business-rules.md`

3. `RequirementsAgent`
- Converts rules into structured modernization requirements.
- Produces: `requirements.md`

4. `SpecAgent`
- Builds the technical solution specification from requirements.
- Produces: `spec.md`

5. `PlanAgent`
- Creates phased execution strategy and milestones.
- Produces: `plan.md`

6. `TaskAgent`
- Breaks the plan into actionable engineering backlog slices.
- Produces: `tasks.md`

7. `MappingMatrixAgent`
- Maps legacy components to modern equivalents and records coverage.
- Produces: `mapping-matrix.md`, `traceability-matrix.md`

8. `TestSpecAgent`
- Defines test strategy and validation criteria from requirements/spec.
- Produces: `test-spec.md`

9. `OpenApiAgent`
- Drafts API contract starter for modernized services.
- Produces: `openapi.yaml`

10. `CopilotPromptAgent`
- Generates implementation prompts for GitHub Copilot.
- Produces: `copilot-build-prompt.md`

11. `QAReviewAgent`
- Creates QA checklist for functional and non-functional validation.
- Produces: `qa-review-checklist.md`

12. `CodeReviewAgent`
- Creates engineering review checklist for architecture/code quality.
- Produces: `code-review-checklist.md`

13. `ReportAgent`
- Summarizes modernization outputs, readiness, and recommended next steps.
- Produces: `modernization-report.md`

## Quick Start

For full run details, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

Fastest option:

```powershell
# Edit .env and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

`run.py` auto-installs required packages from `requirements.txt` before execution (Windows/macOS).

Recommended OpenAI commands:

```powershell
# Edit .env and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

Optional fallback:

```powershell
python run.py --mode ollama
```

1. Optional manual install (runner does this automatically by default):

```powershell
python -m pip install -r requirements.txt
```

2. Place input files under:

- `.agentic-sdlc/examples/inqacc/legacy/cobol`
- `.agentic-sdlc/examples/inqacc/legacy/copybooks`

3. Run pipeline:

```powershell
# Edit .env and set AGENTIC_AI_API_KEY=<YOUR_KEY>
python run.py --mode openai
```

4. Optional dry run:

```powershell
python run_pipeline.py --dry-run
```

## GitHub Copilot Integration

- Generated docs are structured to be consumed directly in Copilot Chat.
- `.github/copilot-instructions.md` enforces implementation constraints at repo level.
- `copilot-build-prompt.md` provides implementation prompts aligned to generated specs/tasks.

## Extend the Framework

### Add a New Agent

1. Create a class in `.agentic-sdlc/agents` extending `BaseAgent`.
2. Define `name`, `purpose`, `input_files`, `output_files`, and `prompt_template`.
3. Export it via `.agentic-sdlc/agents/__init__.py`.
4. Register it in `.agentic-sdlc/orchestrator/pipeline.py`.
5. Add its template in `.agentic-sdlc/templates`.

### Add a New Pipeline

1. Create a YAML file in `.agentic-sdlc/pipelines`.
2. Define pipeline metadata and ordered agent list.
3. Run with `--pipeline <pipeline-name-without-extension>`.
