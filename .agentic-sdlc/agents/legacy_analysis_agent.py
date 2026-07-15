from .base_agent import BaseAgent


class LegacyAnalysisAgent(BaseAgent):
    name = "LegacyAnalysisAgent"
    purpose = "Analyze COBOL programs and copybooks to produce modernization-ready program analysis."
    input_files = ["**/*.cbl", "**/*.cob", "**/*.cpy", "**/*.copybook", "**/*.txt"]
    output_files = ["program-analysis.md"]
    prompt_template = "legacy_analysis_prompt.md"
