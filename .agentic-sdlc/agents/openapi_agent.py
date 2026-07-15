from typing import Dict

from .base_agent import BaseAgent


class OpenApiAgent(BaseAgent):
    name = "OpenApiAgent"
    purpose = "Generate OpenAPI starter contract from requirements and spec artifacts."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["openapi.yaml"]
    prompt_template = "openapi_prompt.md"

    def _generate_content(
        self,
        output_name: str,
        prompt_text: str,
        input_context: Dict[str, str],
        context: Dict[str, str],
    ) -> str:
        service_name = context.get("pipeline_name", "modernization-service").replace("_", "-")
        return (
            "openapi: 3.0.3\n"
            "info:\n"
            f"  title: {service_name}\n"
            "  version: 0.1.0\n"
            "  description: |\n"
            "    Local, template-generated contract for Copilot-driven implementation.\n"
            "    Refine operations and schemas based on requirements.md and spec.md.\n"
            "paths:\n"
            "  /health:\n"
            "    get:\n"
            "      summary: Health endpoint\n"
            "      responses:\n"
            "        '200':\n"
            "          description: OK\n"
            "components:\n"
            "  schemas:\n"
            "    Placeholder:\n"
            "      type: object\n"
            "      additionalProperties: true\n"
            "x-agent:\n"
            f"  name: {self.name}\n"
            "x-prompt-template: |-\n"
            + "\n".join(f"  {line}" for line in prompt_text.splitlines())
            + "\n"
        )
