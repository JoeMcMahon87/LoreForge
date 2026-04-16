# Testing Strategy Reference — LoreForge

Load this file when designing or reviewing tests.

## Framework
pytest
Run: `pytest`

## Testing Pyramid

### Unit Tests
- Test individual pure functions and utilities
- No I/O, no network, no database — mock all dependencies
- Location: `tests/unit/` mirroring the `apps/` structure (e.g. `tests/unit/accounts/test_models.py`)
- Target: all business logic functions, utility functions, data transformers

### Integration Tests
- Test API routes end-to-end with a real (test) database
- Test service functions with real dependencies
- Location: `tests/integration/`
- Target: all API endpoints, all DB operations

### End-to-End Tests
- Simulate real user journeys through the full application
- Tool: pytest + Django test client (v1); upgrade to Playwright post-v1 if needed
- Location: `tests/e2e/`
- Target: critical user flows (login, core feature workflow, settings)

## Validation Checklist (run before every commit)
1. `ruff check . && mypy .` — zero type errors
2. `pytest` — all tests passing
3. Manual walk-through of affected user flows
4. Check that no console errors appear in the browser

## Test Data
# Describe how test data is created and cleaned up

## Do Not
- Test implementation details — test behavior and outcomes
- Skip the manual walk-through step just because tests pass
- Merge with failing tests under any circumstances

---
*Add specific test examples as you build them. Real examples beat abstract rules.*
