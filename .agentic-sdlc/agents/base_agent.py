from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


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
    ) -> None:
        self.templates_dir = templates_dir
        self.input_root = input_root
        self.output_root = output_root
        self.dry_run = dry_run

    def run(self, context: Dict[str, str]) -> AgentResult:
        generated: List[Path] = []
        prompt_text = self._load_prompt_template()
        input_context = self._collect_inputs()

        for output_name in self.output_files:
            target = self.output_root / output_name
            target.parent.mkdir(parents=True, exist_ok=True)
            content = self._generate_content(output_name, prompt_text, input_context, context)
            target.write_text(content, encoding="utf-8")
            generated.append(target)

        self.validate(generated)
        return AgentResult(agent_name=self.name, outputs=generated, dry_run=self.dry_run)

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
        preview_chunks = []
        for name, text in list(input_context.items())[:5]:
            chunk = text[:800].strip()
            preview_chunks.append(f"## Source: {name}\n\n{chunk}\n")

        previews = "\n".join(preview_chunks) if preview_chunks else "No input files found."

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
