from .base_agent import BaseAgent


class QAReviewAgent(BaseAgent):
    name = "QAReviewAgent"
    purpose = "Produce QA verification checklist and report skeleton for generated artifacts."
    input_files = ["**/*.md", "**/*.yaml", "**/*.yml"]
    output_files = ["qa-review-checklist.md"]
    prompt_template = "qa_review_prompt.md"
