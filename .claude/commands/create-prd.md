# /create-prd — Generate Product Requirements Document

Using our conversation so far as context, create a structured PRD for **LoreForge**.

## Before writing, ask clarifying questions about

- Exact user flows and edge cases not yet discussed
- Performance or scale requirements
- Integration constraints (third-party APIs, existing systems)
- Deployment environment specifics
- Any non-functional requirements (accessibility, i18n, security)

The goal: **zero unresolved assumptions** before a single line of code is written.

## PRD Structure

1. **Problem statement** — what problem does this solve, and for whom?
2. **MVP scope** — the minimum feature set for a working v1
3. **Out of scope** — what we are explicitly NOT building right now
4. **Tech stack** — confirmed choices with brief rationale
5. **Directory structure** — top-level file/folder layout
6. **Architecture** — how the pieces connect (data flow, auth, APIs, DB schema)
7. **Phases of work** — ordered list of self-contained implementation phases,
   each small enough to fit in a single PIV loop (half-day to one day of work max)

Save the completed PRD as `PRD.md`.

## One bad assumption in a PRD = hundreds of lines of wrong code.
Take the time to ask. It always pays back.
