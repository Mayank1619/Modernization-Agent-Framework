from __future__ import annotations

from pathlib import Path
import time
from typing import Dict, List, Type

from agents import (
    BusinessRulesAgent,
    CodeReviewAgent,
    CopilotPromptAgent,
    LegacyAnalysisAgent,
    MappingMatrixAgent,
    OpenApiAgent,
    PlanAgent,
    QAReviewAgent,
    ReportAgent,
    RequirementsAgent,
    SpecAgent,
    TaskAgent,
    TestSpecAgent,
)
from agents.base_agent import AgentResult, BaseAgent
from llm.client import LlmClient
from orchestrator.config import PipelineConfig


class PipelineRunner:
    def __init__(
        self,
        pipeline: PipelineConfig,
        templates_dir: Path,
        input_root: Path,
        output_root: Path,
        dry_run: bool = False,
        llm_client: LlmClient | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.templates_dir = templates_dir
        self.input_root = input_root
        self.output_root = output_root
        self.dry_run = dry_run
        self.llm_client = llm_client
        self.registry: Dict[str, Type[BaseAgent]] = {
            "LegacyAnalysisAgent": LegacyAnalysisAgent,
            "BusinessRulesAgent": BusinessRulesAgent,
            "RequirementsAgent": RequirementsAgent,
            "SpecAgent": SpecAgent,
            "PlanAgent": PlanAgent,
            "TaskAgent": TaskAgent,
            "MappingMatrixAgent": MappingMatrixAgent,
            "TestSpecAgent": TestSpecAgent,
            "OpenApiAgent": OpenApiAgent,
            "CopilotPromptAgent": CopilotPromptAgent,
            "QAReviewAgent": QAReviewAgent,
            "CodeReviewAgent": CodeReviewAgent,
            "ReportAgent": ReportAgent,
        }

    def _discover_input_files(self) -> List[str]:
        if not self.input_root.exists():
            return []

        files: List[str] = []
        for path in sorted(self.input_root.rglob("*")):
            if path.is_file():
                files.append(path.relative_to(self.input_root).as_posix())
        return files

    def run(self) -> List[AgentResult]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        context = {"pipeline_name": self.pipeline.name, "dry_run": str(self.dry_run)}
        results: List[AgentResult] = []

        print(f"[INFO] Input root: {self.input_root.as_posix()}")
        input_files = self._discover_input_files()
        if input_files:
            print("[INFO] Inputs detected:")
            for rel_path in input_files:
                print(f"  - {rel_path}")
        else:
            print("[WARN] No input files detected under input root.")

        enabled_steps = [step.name for step in self.pipeline.agents if step.enabled]
        print("[INFO] Agent execution plan:")
        for idx, name in enumerate(enabled_steps, start=1):
            print(f"  {idx}. {name}")

        for step in self.pipeline.agents:
            if not step.enabled:
                print(f"[SKIP] {step.name} (disabled)")
                continue
            agent_cls = self.registry.get(step.name)
            if agent_cls is None:
                raise ValueError(f"Unknown agent '{step.name}' in pipeline '{self.pipeline.name}'")

            print(f"[START] {step.name}")
            start_time = time.perf_counter()
            agent = agent_cls(
                templates_dir=self.templates_dir,
                input_root=self.input_root,
                output_root=self.output_root,
                dry_run=self.dry_run,
                llm_client=self.llm_client,
            )
            try:
                result = agent.run(context)
            except Exception as exc:
                raise RuntimeError(f"Agent failed: {step.name}") from exc

            elapsed_seconds = time.perf_counter() - start_time
            outputs = ", ".join(path.name for path in result.outputs)
            print(f"[DONE] {step.name} ({elapsed_seconds:.2f}s) -> {outputs}")
            results.append(result)

        return results
