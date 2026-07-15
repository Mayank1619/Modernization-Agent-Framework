from .base_agent import BaseAgent


class TestSpecAgent(BaseAgent):
    name = "TestSpecAgent"
    purpose = "Create complete test specifications for business rule and API verification."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["test-spec.md"]
    prompt_template = "test_spec_prompt.md"
