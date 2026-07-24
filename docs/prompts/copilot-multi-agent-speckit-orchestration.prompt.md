# Copilot Multi-Agent Spec Kit Orchestration Prompt

Use this when you want your detailed package-generation style, but split into focused agent slices for stable output quality.

## Objective

Produce a modernization package with output quality equivalent to the current Spec Kit artifacts while avoiding under-detail and over-detail drift.

## Authority Order

1. Imported Spec Kit bundle at <SPEC_KIT_IMPORT_PATH>
2. manifest.json entrypoints from that bundle
3. Legacy source assets in the working package
4. Existing repository governance instructions

Never invent fields. Clearly mark evidence, inference, and assumptions.

## Execution Model

Run in sequence. Each step writes only its owned artifacts. Do not rewrite downstream artifacts early.

### Phase A: Evidence and Rule Foundation

1. LegacyAnalysisAgent
- Generate: supporting/program-analysis.md, supporting/dependency-map.md
- Must include: program purpose, inputs/outputs, dependencies, control flow, error/success paths, ambiguities
- Every claim tagged as Evidence, Inference, or Assumption

2. BusinessRulesAgent
- Generate: supporting/business-rules.md
- Must include per rule: Rule ID, source evidence, rule description, modern interpretation, priority, risk, testability

3. RequirementsAgent
- Generate: supporting/requirements.md
- Must include FR/NFR/AC/ASM IDs and explicit modernization enhancements separated from preserved legacy behavior

Gate A:
- Every FR maps to at least one BR
- Every BR has source evidence citation

### Phase B: Target Design and Contracts

4. SystemIntentAgent
- Generate or update: intended-system.md
- Constrain target stack, security baseline, runtime, and integration boundaries

5. SpecAgent
- Generate: spec.md
- Must include behavior, acceptance criteria, traceability to business rules, edge cases, non-goals

6. OpenApiAgent
- Generate: contracts/openapi.yaml
- Must be consistent with spec.md and mapping matrix only

7. MappingMatrixAgent
- Generate: supporting/mapping-matrix.md, supporting/traceability-matrix.md
- Mark unclear links as SME validation required

Gate B:
- AC links to FR
- API fields all trace to mapping matrix and copybook or requirement evidence
- No orphan schemas

### Phase C: Delivery Readiness

8. PlanAgent
- Generate: plan.md
- Must include architecture transition, adapter boundary, testing strategy, deployment strategy, and risk mitigation

9. TaskAgent
- Generate: tasks.md
- Every TASK links to FR/AC/BR and is implementation-actionable

10. TestSpecAgent
- Generate: supporting/test-spec.md
- Every TC maps to BR and FR or AC

11. QAReviewAgent
- Generate: supporting/qa-review-checklist.md

12. CodeReviewAgent
- Generate: supporting/code-review-checklist.md

13. ReportAgent
- Generate: supporting/modernization-report.md

Gate C:
- Run project review command: <SPEC_KIT_REVIEW_COMMAND>
- Run detail drift validator:
  - python scripts/validate_detail_drift.py --generated-output .agentic-sdlc/examples/inqacc/output --bundle-specs <SPEC_KIT_IMPORT_PATH>/specs
- Fix only in-scope findings and rerun both checks

## Output Contract

Return summary in this exact structure:

1. Bundle applied summary
2. Agents executed and artifacts produced
3. Traceability coverage summary (BR->FR->AC->TASK->TC->API)
4. Review result (pass or fail + key findings)
5. Detail drift result (pass or fail + failed artifacts)
6. Remaining SME validation items
7. Blockers

## Strict Constraints

- Do not add random behavior, fields, or APIs
- Keep spec as source of truth for implementation
- Preserve observable legacy behavior unless explicitly marked modernization enhancement
- Keep controllers thin and business logic in services when generating implementation prompts
- Use repository interfaces and mock adapters in POC mode

## Optional Parallelization Rule

Only these pairs can run in parallel after dependencies are complete:
- QAReviewAgent with CodeReviewAgent
- PlanAgent with early draft of TaskAgent, then TaskAgent must reconcile to final plan

All other phases run sequentially to protect traceability quality.
