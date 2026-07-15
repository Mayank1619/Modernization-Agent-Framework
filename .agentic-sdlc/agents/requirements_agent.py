from .base_agent import BaseAgent


class RequirementsAgent(BaseAgent):
    name = "RequirementsAgent"
    purpose = "Produce structured requirements from business rules and legacy findings."
    input_files = ["**/*.md", "**/*.cbl", "**/*.cob", "**/*.cpy"]
    output_files = ["requirements.md"]
    prompt_template = "requirements_prompt.md"
