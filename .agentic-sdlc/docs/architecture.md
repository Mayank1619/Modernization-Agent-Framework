# Agentic SDLC Framework Architecture

## Goal

Provide a local, repository-based agentic framework for:
- Spec-Driven Development (SDD)
- Mainframe modernization analysis
- Copilot-assisted implementation planning

## Building Blocks

- Agents: Python classes that transform input context into output artifacts.
- Templates: Markdown prompt templates consumed by each agent.
- Pipelines: YAML files declaring ordered agent execution.
- Orchestrator: Loads pipeline config and executes agents sequentially.
- Dual-run Orchestrator: Executes primary and Claude runs, then merges artifacts.
- Demo dual-run mode: Simulates primary, Claude, and merge phases without AI keys.
- LLM Clients: Ollama, OpenAI-compatible, and Claude HTTP clients.
- Visual API: FastAPI layer for run lifecycle, events, and artifact retrieval.
- Visual Dashboard: React UI for run control and real-time status visualization.
- Artifacts: Markdown and YAML outputs used by engineers and Copilot.

## Execution Model

1. User places input legacy artifacts in example or project input folder.
2. User runs run_pipeline.py or starts a run from the Visual API/UI.
3. PipelineRunner instantiates each configured agent.
4. Each agent loads template, gathers inputs, writes output artifact files.
5. Event sink records run and agent lifecycle updates.
6. Generated artifacts are reviewed and refined with Copilot in VS Code.

## Dual-Model Execution Model

1. Run primary model pipeline into output_primary.
2. Run Claude model pipeline into output_claude.
3. Compare artifacts by filename.
4. Merge core artifacts with LLM-assisted reconciliation.
5. Select non-core artifacts using deterministic detail heuristics.
6. Write final merged outputs to output and publish dual-model-analysis.md.

## Demo Dual-Phase Model

1. Run primary phase in dry-run mode.
2. Run Claude phase in dry-run mode.
3. Merge outputs heuristically into final output.
4. Emit full phase telemetry for UI and API consumers.

## Visual Run Flow

1. UI posts run request to `/api/runs/start`.
2. API launches background run thread and stores run metadata.
3. UI polls `/api/runs/{run_id}` for status and events.
4. UI reads generated files via artifact endpoints.
5. UI displays elapsed timer and allows Classic/Neon theme switching.

## Design Principles

- Local-first operation with optional cloud LLM integrations
- Deterministic dry-run support for offline artifact scaffolding
- Simple modular classes and explicit pipeline ordering
- Transparent generated artifacts and comparison reporting
- Favor faster feedback through parallel dual runs and prompt context budgeting
- Easy extension through new agents, providers, and pipelines
