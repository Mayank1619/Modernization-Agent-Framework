from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from llm.client import LlmClient


@dataclass
class AgentResult:
    agent_name: str
    outputs: List[Path]
    dry_run: bool


class BaseAgent:
    name: str = "BaseAgent"
    purpose: str = "Base class for local, template-driven SDLC agents."
    input_files: List[str] = []
    output_files: List[str] = []
    prompt_template: str = ""

    def __init__(
        self,
        templates_dir: Path,
        input_root: Path,
        output_root: Path,
        dry_run: bool = False,
        llm_client: LlmClient | None = None,
    ) -> None:
        self.templates_dir = templates_dir
        self.input_root = input_root
        self.output_root = output_root
        self.dry_run = dry_run
        self.llm_client = llm_client

    def run(self, context: Dict[str, str]) -> AgentResult:
        generated: List[Path] = []
        prompt_text = self._load_prompt_template()
        input_context = self._collect_inputs()
        input_context = self._augment_input_context_with_context_files(input_context, context)

        for output_name in self.output_files:
            target = self.output_root / output_name
            target.parent.mkdir(parents=True, exist_ok=True)
            content = self._generate_content(output_name, prompt_text, input_context, context)
            target.write_text(content, encoding="utf-8")
            generated.append(target)

        self.validate(generated)
        return AgentResult(agent_name=self.name, outputs=generated, dry_run=self.dry_run)

    def _augment_input_context_with_context_files(
        self, input_context: Dict[str, str], context: Dict[str, str]
    ) -> Dict[str, str]:
        system_intent_path = context.get("system_intent_path", "").strip()
        if not system_intent_path:
            return input_context

        resolved = Path(system_intent_path)
        if not resolved.exists() or not resolved.is_file():
            return input_context

        enriched = dict(input_context)
        enriched["provided/system-intent.md"] = resolved.read_text(
            encoding="utf-8", errors="ignore"
        )
        return enriched

    def validate(self, outputs: Iterable[Path]) -> None:
        for output in outputs:
            if not output.exists():
                raise FileNotFoundError(f"{self.name} failed to create output file: {output}")
            if output.stat().st_size == 0:
                raise ValueError(f"{self.name} created an empty output file: {output}")

    def _load_prompt_template(self) -> str:
        if not self.prompt_template:
            return ""

        template_path = self.templates_dir / self.prompt_template
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found for {self.name}: {template_path}"
            )
        return template_path.read_text(encoding="utf-8")

    def _collect_inputs(self) -> Dict[str, str]:
        collected: Dict[str, str] = {}
        for pattern in self.input_files:
            for file_path in sorted(self.input_root.rglob(pattern)):
                if file_path.is_file():
                    rel = file_path.relative_to(self.input_root).as_posix()
                    collected[rel] = file_path.read_text(encoding="utf-8", errors="ignore")

        # Make prior generated artifacts available to downstream agents.
        if self.output_root.exists():
            for file_path in sorted(self.output_root.glob("*.md")):
                rel = f"output/{file_path.name}"
                collected[rel] = file_path.read_text(encoding="utf-8", errors="ignore")
            for file_path in sorted(self.output_root.glob("*.yaml")):
                rel = f"output/{file_path.name}"
                collected[rel] = file_path.read_text(encoding="utf-8", errors="ignore")

        return collected

    def _generate_content(
        self,
        output_name: str,
        prompt_text: str,
        input_context: Dict[str, str],
        context: Dict[str, str],
    ) -> str:
        dry_run_marker = "DRY RUN" if self.dry_run else "READY FOR COPILOT"
        files_list = "\n".join(f"- {name}" for name in input_context.keys()) or "- None"
        prioritized_items = self._prioritize_input_context(input_context)
        preview_chunks = []
        for name, text in prioritized_items[:20]:
            chunk = text[:2500].strip()
            preview_chunks.append(f"## Source: {name}\n\n{chunk}\n")

        previews = "\n".join(preview_chunks) if preview_chunks else "No input files found."

        if not self.dry_run and self.llm_client is not None:
            system_prompt = (
                "You are an enterprise software modernization and Spec-Driven Development "
                "assistant. Produce only the target artifact content, with no preamble. "
                "Stay faithful to provided legacy inputs and do not invent fields. "
                "Provide implementation-ready detail with stable headings and explicit IDs "
                "for requirements, rules, and tests where applicable."
            )
            user_prompt = (
                f"Agent Name: {self.name}\n"
                f"Purpose: {self.purpose}\n"
                f"Target Output File: {output_name}\n"
                f"Pipeline: {context.get('pipeline_name', 'unknown')}\n\n"
                "Intended System Notes:\n"
                "- If `provided/system-intent.md` exists, treat it as mandatory target architecture.\n"
                "- Keep all outputs consistent with intended stack, versions, security, and constraints.\n\n"
                "Prompt Template:\n"
                f"{prompt_text}\n\n"
                "Input Files:\n"
                f"{files_list}\n\n"
                "Input Preview Snippets:\n"
                f"{previews}\n"
            )
            return self.llm_client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        return (
            f"# {output_name}\n\n"
            f"Status: {dry_run_marker}\n\n"
            f"Agent: {self.name}\n"
            f"Purpose: {self.purpose}\n\n"
            f"## Pipeline Context\n\n"
            f"- Pipeline: {context.get('pipeline_name', 'unknown')}\n"
            f"- Input Root: {self.input_root.as_posix()}\n"
            f"- Output Root: {self.output_root.as_posix()}\n\n"
            f"## Inputs Considered\n\n"
            f"{files_list}\n\n"
            f"## Prompt Template\n\n"
            f"{prompt_text}\n\n"
            f"## Input Previews\n\n"
            f"{previews}\n"
        )

    def _priority_for_file(self, name: str) -> int:
        lowered = name.lower()

        if "intended-system" in lowered or "system-intent" in lowered:
            return 0
        if lowered.endswith((".cbl", ".cob")):
            return 1
        if lowered.endswith((".cpy", ".copybook")):
            return 2
        if lowered.endswith("output/business-rules.md"):
            return 3
        if lowered.endswith("output/requirements.md"):
            return 4
        if lowered.endswith("output/spec.md"):
            return 5
        if lowered.endswith("output/openapi.yaml"):
            return 6
        if lowered.endswith((".yaml", ".yml")):
            return 7
        if lowered.endswith(".md"):
            return 8
        return 9

    def _prioritize_input_context(
        self, input_context: Dict[str, str]
    ) -> List[tuple[str, str]]:
        return sorted(
            input_context.items(),
            key=lambda item: (self._priority_for_file(item[0]), item[0]),
        )
