# /commit — Create a Knowledge-Rich Commit

Create a git commit for the current changes.

## Format
```
[type]: [concise description]

[body]
```

Types: `feat` `fix` `refactor` `test` `docs` `chore`

## Body must include

- **What was implemented** (1–3 sentences)
- **Key decisions made** and the reasoning behind them
- **Gotchas or non-obvious behaviors** introduced
- **Anything future sessions should know** about this change

## Why this matters
Your commit history is your long-term memory.
Write each message as if explaining to your future self six months from now.
The `/prime` command reads `git log` — rich commits make future sessions smarter.
