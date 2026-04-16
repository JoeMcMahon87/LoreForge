# LoreForge — AI Development System

This project uses a three-layer integrated AI development system.

## Quick Start

```bash
# Open Claude Code in this directory
claude

# Start every session with:
/prime

# Begin a new feature:
/plan-feature [description]

# After planning, in a NEW session:
/execute plans/[feature-name].md

# After validation:
/commit
```

## System Overview

### Layer 1: PIV Loop (always active)
- `AGENTS.md` — project rules loaded every session
- `PRD.md` — what we're building
- `.claude/commands/` — reusable workflow commands
- `reference/` — on-demand context docs

### Layer 2: Knowledge Base

```bash
# Session hooks run automatically via .claude/settings.json
# Flush daily logs to wiki:
python scripts/flush.py

# Health check the KB:
# Run /kb-lint in Claude Code
```

### Layer 3: Archon Harness (Workflow Orchestration)

```bash
# Workflows live in archon/workflows/
# Run from Claude Code: "use Archon to fix issue #N"
# Dashboard: http://localhost:5178
```

## Key Principle: Context is Precious
- Plan in one session. Implement in a **new session** with only the plan.
- `AGENTS.md` stays under 250 lines. Everything else lives in `reference/`.
- Every bug → update `AGENTS.md` or `reference/` so it doesn't recur.

## File Map
```
LoreForge/
├── AGENTS.md                    ← global rules (always loaded)
├── PRD.md                       ← what we're building
├── .claude/
│   ├── settings.json            ← hook configuration
│   └── commands/                ← /prime, /create-prd, /plan-feature, /execute, /commit
├── reference/                   ← on-demand context docs
├── plans/                       ← structured feature plans
├── knowledge/                   ← KB: daily-logs/, wiki/, index.md, log.md
├── scripts/                     ← flush.py, hooks/
└── archon/workflows/            ← YAML harness definitions
```

## References
- [Archon](https://github.com/coleam00/archon) — harness builder
- [Claude Memory Compiler](https://github.com/coleam00/claude-memory-compiler) — KB system
- [Dead Simple Framework](https://github.com/coleam00/link-in-bio-page-builder) — PIV loop
