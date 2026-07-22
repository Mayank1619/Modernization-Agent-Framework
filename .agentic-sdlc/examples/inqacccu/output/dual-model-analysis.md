# Dual-Model Comparison Analysis

This report compares primary-model and Claude-model artifacts and records how final outputs were selected.

| Artifact | Status | Selected | Primary chars | Claude chars | Merged chars | Notes |
|---|---|---|---:|---:|---:|---|
| business-rules.md | merged | llm-merge | 3072 | 14176 | 14174 | Combined non-overlapping detail and resolved conflicts. |
| code-review-checklist.md | selected | secondary | 2168 | 14528 | 14528 | Selected higher-detail variant using markdown/table/length heuristic. |
| copilot-build-prompt.md | selected | secondary | 4006 | 14905 | 14905 | Selected higher-detail variant using markdown/table/length heuristic. |
| intended-system.md | selected | secondary | 3030 | 14259 | 14259 | Selected higher-detail variant using markdown/table/length heuristic. |
| mapping-matrix.md | merged | llm-merge | 2761 | 12401 | 13935 | Combined non-overlapping detail and resolved conflicts. |
| modernization-report.md | selected | secondary | 3126 | 15131 | 15131 | Selected higher-detail variant using markdown/table/length heuristic. |
| openapi.yaml | merged | llm-merge | 3501 | 16555 | 16556 | Combined non-overlapping detail and resolved conflicts. |
| plan.md | selected | secondary | 3045 | 14308 | 14308 | Selected higher-detail variant using markdown/table/length heuristic. |
| program-analysis.md | selected | secondary | 4523 | 12822 | 12822 | Selected higher-detail variant using markdown/table/length heuristic. |
| qa-review-checklist.md | selected | secondary | 3783 | 13521 | 13521 | Selected higher-detail variant using markdown/table/length heuristic. |
| requirements.md | merged | llm-merge | 4212 | 14738 | 15412 | Combined non-overlapping detail and resolved conflicts. |
| spec.md | merged | llm-merge | 4017 | 13936 | 14014 | Combined non-overlapping detail and resolved conflicts. |
| tasks.md | selected | secondary | 4114 | 15426 | 15426 | Selected higher-detail variant using markdown/table/length heuristic. |
| test-spec.md | merged | llm-merge | 4472 | 13953 | 6232 | Combined non-overlapping detail and resolved conflicts. |
| traceability-matrix.md | merged | llm-merge | 2239 | 12057 | 14015 | Combined non-overlapping detail and resolved conflicts. |
