#!/usr/bin/env python3
"""
Session end / pre-compact hook — summarizes the session into a daily log entry.
Requires Claude Code CLI (uses your Anthropic subscription, no separate API key).
Configured in .claude/settings.json under hooks.sessionEnd and hooks.preCompact.
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

transcript = sys.stdin.read()
if not transcript.strip():
    sys.exit(0)

PROMPT = """
Summarize this Claude Code session as a structured knowledge log entry.

Include:
- **Session goal**: What were we trying to accomplish?
- **Key decisions**: Architectural or design choices made and the reasoning
- **Lessons learned**: What worked, what didn't, what to watch out for
- **Code patterns established**: Any new conventions or patterns introduced
- **Action items**: Anything that should be done in a future session
- **KB update suggestions**: Existing wiki articles that should be revised or new ones to create

Be specific. This entry will be read by your future self.
Write in past tense. Focus on decisions and lessons — not a blow-by-blow account.
"""

result = subprocess.run(
    ["claude", "-p", PROMPT],
    input=transcript,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"Warning: session capture failed: {result.stderr}", file=sys.stderr)
    sys.exit(0)

log_dir = Path("knowledge/daily-logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"{date.today().isoformat()}.md"

with open(log_file, "a") as f:
    f.write(f"\n\n---\n\n{result.stdout}")

print(f"Session captured → {log_file}", file=sys.stderr)
