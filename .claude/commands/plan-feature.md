# /plan-feature — Create a Structured Feature Plan

Create a detailed implementation plan for the current phase or feature.

## Steps

1. Re-read the relevant section of `PRD.md`.
2. Explore existing code to understand what's already built.
3. Spin off a sub-agent to research any external docs, libraries, or APIs needed.
   (Sub-agents keep research context isolated — only the summary comes back.)
   - Read relevant `knowledge/wiki/` articles for this feature area.
4. Draft the plan and save it as `plans/[feature-slug].md`.
5. Ask me to review before we proceed to implementation.

## Plan Structure

```markdown
## Goal
[One sentence: what does success look like for this feature?]

## Context
- Affected files: [list]
- External docs to reference: [list]
- Dependencies or env vars needed: [list]

## Task List
1. [Specific task — name the file to create or modify]
2. ...

## Environment Setup
[Any .env vars, dependencies, or config to set up BEFORE coding begins]

## Validation Strategy
Step-by-step verification, written as if explaining to a QA engineer:
- Type checks: `ruff check . && mypy .`
- Unit tests: `pytest`
- Integration tests: [specific scenarios]
- Manual user journeys: [exact steps to walk through in the browser/CLI]
```

## Context reset reminder
After this plan is reviewed and approved, start a **fresh session** and pass
only the plan file to `/execute`. Do not carry this planning conversation forward.
