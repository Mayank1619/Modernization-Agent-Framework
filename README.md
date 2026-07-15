# Agentic SDLC Framework for Spec-Driven Development and Mainframe Modernization

## What This Framework Does

This repository provides a local, repo-based multi-agent framework that converts business requests and legacy source code into a full delivery artifact set for modernization and Spec-Driven Development.

Generated artifacts include:

- program-analysis.md
- business-rules.md
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

## How It Supports Spec-Driven Development

- Structures delivery around requirements.md, spec.md, and traceability artifacts.
- Creates explicit mappings from legacy sources to modern implementation artifacts.
- Produces test and review checklists aligned with business rules.
- Enables progressive refinement with humans and Copilot in the loop.

## GitHub Copilot Integration

- Prompt templates and generated artifacts are designed for direct copy/paste into Copilot chat.
- Repository-level instructions in .github/copilot-instructions.md enforce architecture and behavior constraints.
- copilot-build-prompt.md provides implementation-ready prompts tied to generated specs.

## Run the Mainframe Modernization Pipeline

For a complete runbook, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

1. Place legacy files under:
   - .agentic-sdlc/examples/inqacc/legacy/cobol
   - .agentic-sdlc/examples/inqacc/legacy/copybooks

2. Run:

python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output

3. Dry-run mode:

python run_pipeline.py --pipeline mainframe_modernization --input .agentic-sdlc/examples/inqacc/legacy --output .agentic-sdlc/examples/inqacc/output --dry-run

## Add a New Agent

1. Create a new class in .agentic-sdlc/agents extending BaseAgent.
2. Define:
   - name
   - purpose
   - input_files
   - output_files
   - prompt_template
3. Add the class to .agentic-sdlc/agents/__init__.py.
4. Register the class in .agentic-sdlc/orchestrator/pipeline.py.
5. Add a template in .agentic-sdlc/templates.

## Add a New Pipeline

1. Create a YAML file under .agentic-sdlc/pipelines.
2. Define pipeline name, description, and ordered agent steps.
3. Run with --pipeline <filename-without-extension>.

## Use Generated Prompts in Copilot

1. Open generated artifacts in VS Code.
2. Copy sections from copilot-build-prompt.md.
3. Ask Copilot to implement one task slice at a time from tasks.md.
4. Validate outputs against spec.md, mapping-matrix.md, and test-spec.md.
