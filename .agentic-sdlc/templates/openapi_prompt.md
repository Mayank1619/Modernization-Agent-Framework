# OpenAPI Prompt

Generate an OpenAPI contract skeleton based on requirements and specification.

Inputs must include `intended-system.md` when available.

Include:
- Core resources and operations
- Request/response schemas
- Error payload schema
- Versioning notes

Minimum detail expectations:
- Use OpenAPI 3.0.3 or higher.
- Include at least one business endpoint derived from spec, not only health checks.
- Include input validation constraints (patterns, required fields, enums, bounds).
- Include security scheme section and error response structure.
- Ensure schema fields map to requirements/spec and avoid invented legacy fields.
