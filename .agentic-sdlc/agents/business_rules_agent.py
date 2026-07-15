from .base_agent import BaseAgent


class BusinessRulesAgent(BaseAgent):
    name = "BusinessRulesAgent"
    purpose = "Extract and normalize business rules from legacy analysis and source artifacts."
    input_files = ["**/*.cbl", "**/*.cob", "**/*.cpy", "**/*.md"]
    output_files = ["business-rules.md"]
    prompt_template = "business_rules_prompt.md"
