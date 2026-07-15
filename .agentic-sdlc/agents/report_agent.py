from .base_agent import BaseAgent


class ReportAgent(BaseAgent):
    name = "ReportAgent"
    purpose = "Compile a final modernization report that summarizes outputs and next actions."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["modernization-report.md"]
    prompt_template = "report_prompt.md"
