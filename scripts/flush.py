#!/usr/bin/env python3
"""
Flush script — promotes recent daily logs into structured wiki articles.
Run manually or via cron once per day.

Usage:
    python scripts/flush.py              # process last 3 days
    python scripts/flush.py --days 7     # process last 7 days
"""
import argparse
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--days", type=int, default=3)
args = parser.parse_args()

log_dir = Path("knowledge/daily-logs")
recent_logs = []

for i in range(args.days):
    d = date.today() - timedelta(days=i)
    f = log_dir / f"{d.isoformat()}.md"
    if f.exists():
        recent_logs.append(f"### {d.isoformat()}\n{f.read_text()}")

if not recent_logs:
    print("No recent logs to flush.")
    sys.exit(0)

combined = "\n\n".join(recent_logs)

index_path = Path("knowledge/index.md")
existing_index = index_path.read_text() if index_path.exists() else "(empty)"

PROMPT = f"""
You are maintaining the knowledge base for the project "LoreForge".

Recent session logs:
{combined}

Current wiki index:
{existing_index}

Your tasks:

1. Identify 2–5 knowledge items from the logs worth promoting into permanent wiki articles.
   Prioritize: architectural decisions, recurring patterns, non-obvious lessons, gotchas,
   integration details. Skip trivial implementation details.

2. For each item, create a structured wiki article. Save to the correct subfolder:
   - knowledge/wiki/concepts/[slug].md      — patterns, abstractions, key ideas
   - knowledge/wiki/decisions/[slug].md     — "why we chose X over Y"
   - knowledge/wiki/connections/[slug].md   — "how X relates to Y"

3. Update knowledge/index.md — add a one-line entry for each new article.

4. Append to knowledge/log.md for each article created:
   ## [YYYY-MM-DD] flush | Created: [article title]

Wiki article format:
---
title: [Title]
created: 2026-04-16
sources: [list of daily log dates]
---

# [Title]

[2–3 sentence summary]

## Context
[When and why this knowledge matters]

## Details
[The substance]

## Related
[Links to other wiki articles, if relevant]
"""

result = subprocess.run(
    ["claude", "-p", PROMPT],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"Flush failed: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print(result.stdout)
print("\n✓ Flush complete — check knowledge/wiki/ for new articles.")
