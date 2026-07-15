from .base_agent import BaseAgent


class MappingMatrixAgent(BaseAgent):
    name = "MappingMatrixAgent"
    purpose = "Create mapping and traceability matrices from requirements through implementation."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml", "**/*.cbl", "**/*.cpy"]
    output_files = ["mapping-matrix.md", "traceability-matrix.md"]
    prompt_template = "mapping_matrix_prompt.md"
