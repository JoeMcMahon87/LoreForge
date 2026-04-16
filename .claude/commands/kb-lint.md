# /kb-lint — Knowledge Base Health Check

Perform a health check on the knowledge base at `knowledge/`.

## Check for

- **Contradictions**: articles that conflict with each other → flag for manual review
- **Stale content**: articles referencing decisions we've since reversed → mark outdated
- **Orphans**: wiki articles with no inbound links from other articles or the index
- **Missing articles**: important topics mentioned in daily logs but never wikified
- **Knowledge gaps**: areas where the agent consistently asks questions KB should answer
- **Index drift**: articles in `wiki/` not yet listed in `index.md`

## Output

A prioritized list of improvements with suggested actions.

**Do not make changes.** Output recommendations only — I will review and approve
all changes to the KB manually. The AI layer is mine to control.
