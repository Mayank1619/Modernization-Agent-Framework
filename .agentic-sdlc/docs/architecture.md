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
- Artifacts: Markdown and YAML outputs used by engineers and Copilot.

## Execution Model

1. User places input legacy artifacts in example or project input folder.
2. User runs run_pipeline.py with pipeline name, input, and output paths.
3. PipelineRunner instantiates each configured agent.
4. Each agent loads template, gathers inputs, writes output artifact files.
5. Generated artifacts are reviewed and refined with Copilot in VS Code.

## Design Principles

- No cloud dependency
- No external API calls
- Simple modular classes
- Transparent generated artifacts
- Easy extension through new agents and pipelines
