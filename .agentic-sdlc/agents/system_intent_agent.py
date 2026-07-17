from .base_agent import BaseAgent


class SystemIntentAgent(BaseAgent):
    name = "SystemIntentAgent"
    purpose = (
        "Define intended target system architecture and constraints "
        "before downstream requirement and spec generation."
    )
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml", "**/*.cbl", "**/*.cob", "**/*.cpy"]
    output_files = ["intended-system.md"]
    prompt_template = "system_intent_prompt.md"
