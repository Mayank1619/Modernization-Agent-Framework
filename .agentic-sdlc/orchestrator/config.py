from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class AgentStep:
    name: str
    enabled: bool = True


@dataclass
class PipelineConfig:
    name: str
    description: str
    agents: List[AgentStep]


def load_pipeline_config(config_path: Path) -> PipelineConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Pipeline config not found: {config_path}")

    raw: Dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not raw:
        raise ValueError(f"Pipeline config is empty: {config_path}")

    name = raw.get("name")
    description = raw.get("description", "")
    raw_agents = raw.get("agents", [])

    if not name:
        raise ValueError(f"Pipeline config missing required field 'name': {config_path}")
    if not isinstance(raw_agents, list) or not raw_agents:
        raise ValueError(f"Pipeline config must define a non-empty 'agents' list: {config_path}")

    agents = [
        AgentStep(name=item["name"], enabled=item.get("enabled", True))
        for item in raw_agents
        if "name" in item
    ]

    if not agents:
        raise ValueError(f"No valid agent entries in pipeline: {config_path}")

    return PipelineConfig(name=name, description=description, agents=agents)
