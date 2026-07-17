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
- LLM Clients: Ollama, OpenAI-compatible, and Claude HTTP clients.
- Artifacts: Markdown and YAML outputs used by engineers and Copilot.

## Execution Model

1. User places input legacy artifacts in example or project input folder.
2. User runs run_pipeline.py with pipeline name, input, and output paths.
3. PipelineRunner instantiates each configured agent.
4. Each agent loads template, gathers inputs, writes output artifact files.
5. Generated artifacts are reviewed and refined with Copilot in VS Code.

## Dual-Model Execution Model

1. Run primary model pipeline into output_primary.
2. Run Claude model pipeline into output_claude.
3. Compare artifacts by filename.
4. Merge core artifacts with LLM-assisted reconciliation.
5. Select non-core artifacts using deterministic detail heuristics.
6. Write final merged outputs to output and publish dual-model-analysis.md.

## Design Principles

- Local-first operation with optional cloud LLM integrations
- Deterministic dry-run support for offline artifact scaffolding
- Simple modular classes and explicit pipeline ordering
- Transparent generated artifacts and comparison reporting
- Easy extension through new agents, providers, and pipelines
