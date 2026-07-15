from __future__ import annotations

from pathlib import Path
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

    def run(self) -> List[AgentResult]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        context = {"pipeline_name": self.pipeline.name, "dry_run": str(self.dry_run)}
        results: List[AgentResult] = []

        for step in self.pipeline.agents:
            if not step.enabled:
                continue
            agent_cls = self.registry.get(step.name)
            if agent_cls is None:
                raise ValueError(f"Unknown agent '{step.name}' in pipeline '{self.pipeline.name}'")

            agent = agent_cls(
                templates_dir=self.templates_dir,
                input_root=self.input_root,
                output_root=self.output_root,
                dry_run=self.dry_run,
                llm_client=self.llm_client,
            )
            results.append(agent.run(context))

        return results
