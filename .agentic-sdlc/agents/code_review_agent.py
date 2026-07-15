from .base_agent import BaseAgent


class CodeReviewAgent(BaseAgent):
    name = "CodeReviewAgent"
    purpose = "Produce code review checklist and architecture conformance report skeleton."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["code-review-checklist.md"]
    prompt_template = "code_review_prompt.md"
