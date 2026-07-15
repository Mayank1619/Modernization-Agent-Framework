from .base_agent import BaseAgent


class SpecAgent(BaseAgent):
    name = "SpecAgent"
    purpose = "Generate implementation-ready functional and technical specification."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["spec.md"]
    prompt_template = "spec_prompt.md"
