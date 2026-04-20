# Knowledge Base Index — LoreForge
Last updated: (auto-maintained by flush script)

This file is loaded at the start of every coding session.
Use it to navigate to relevant articles before answering questions or making decisions.

## Concepts
*(Key patterns, abstractions, and architectural ideas — populated after first flush)*

## Architectural Decisions

- [Custom User Model](wiki/decisions/custom-user-model.md) — AUTH_USER_MODEL set before first migration; role field (admin/gm/player)
- [Test Settings — SQLite vs PostgreSQL](wiki/decisions/test-settings.md) — tests use SQLite :memory:; PostgreSQL-specific tests need dev settings
- [World Permission Mixins](wiki/decisions/world-permission-mixins.md) — GMMixin, WorldOwnerMixin, WorldMemberMixin pattern; dispatch order matters
- [CampaignForm Status Field](wiki/decisions/campaign-form-status-field.md) — status not required in form; template hides it on create

## Patterns and Conventions
*(Code patterns specific to this codebase — populated after first flush)*

## Known Issues and Workarounds
*(Gotchas, non-obvious behaviors, known limitations — populated after first flush)*

## External Integrations
*(Notes on third-party APIs, services, and SDKs we use — populated after first flush)*

---
*Auto-maintained by `scripts/flush.py`. Do not edit manually — changes will be overwritten.*
*To add an article: write it to `knowledge/wiki/[category]/[slug].md`,
then add a one-line entry here.*
