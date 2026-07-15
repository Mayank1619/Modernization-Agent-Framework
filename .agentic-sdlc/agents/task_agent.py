from .base_agent import BaseAgent


class TaskAgent(BaseAgent):
    name = "TaskAgent"
    purpose = "Generate actionable engineering tasks aligned to the delivery plan."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["tasks.md"]
    prompt_template = "tasks_prompt.md"
