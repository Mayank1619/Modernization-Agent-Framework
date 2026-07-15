from .base_agent import BaseAgent


class CopilotPromptAgent(BaseAgent):
    name = "CopilotPromptAgent"
    purpose = "Generate implementation prompts that can be pasted directly into GitHub Copilot."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["copilot-build-prompt.md"]
    prompt_template = "copilot_implementation_prompt.md"
