#!/usr/bin/env python3
"""
Session start hook — loads AGENTS.md and knowledge/index.md into context.
Configured in .claude/settings.json under hooks.sessionStart.
"""
import sys
from pathlib import Path

parts = []

agents = Path("AGENTS.md")
if agents.exists():
    parts.append(f"## Project Rules\n{agents.read_text()}")

index = Path("knowledge/index.md")
if index.exists():
    parts.append(f"## Knowledge Base Index\n{index.read_text()}")
else:
    parts.append("## Knowledge Base\nNo index yet — this is a new project.")

# Output to stdout; Claude Code injects this as additional system context
print("\n\n".join(parts))
