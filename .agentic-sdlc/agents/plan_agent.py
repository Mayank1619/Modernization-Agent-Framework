from .base_agent import BaseAgent


class PlanAgent(BaseAgent):
    name = "PlanAgent"
    purpose = "Build phased modernization and delivery plan from the approved specification."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["plan.md"]
    prompt_template = "plan_prompt.md"
