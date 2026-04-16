# /execute — Implementation Session

Execute the implementation plan passed as an argument.

## Usage
`/execute plans/[feature-slug].md`

## Rules

1. Read the plan file in full before writing any code.
2. Follow the task list in order. Verify each task before moving to the next.
3. Set up environment variables / dependencies listed in the plan before coding.
4. When implementation is complete, run the full validation strategy from the plan:
   - `ruff check . && mypy .`
   - `pytest`
   - Walk through the manual user journeys
5. Do not ask questions during implementation unless you hit a genuine blocker
   that cannot be resolved from the plan, codebase, or `AGENTS.md`.
6. Report back only when **all validations pass**.

## On failure
If a validation step fails, diagnose and fix before reporting done.
Do not declare success with failing tests or type errors.
7. After validation, update `knowledge/` with any new decisions or patterns.
