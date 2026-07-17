from .base_agent import BaseAgent


class OpenApiAgent(BaseAgent):
    name = "OpenApiAgent"
    purpose = "Generate OpenAPI starter contract from requirements and spec artifacts."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["openapi.yaml"]
    prompt_template = "openapi_prompt.md"
