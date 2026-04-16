# API Patterns Reference — LoreForge

Load this file when building or modifying API routes or service functions.

## Route Structure
- Base path: /api
- Convention: REST — `GET /resource`, `POST /resource`, `PATCH /resource/:id`, `DELETE /resource/:id`

## Standard Response Shape
```json
// Success
{ "data": ..., "error": null }

// Error
{ "data": null, "error": { "code": "ERROR_CODE", "message": "Human message" } }
```

## Authentication
JWT tokens, stored in httpOnly cookies

## Validation
- Validate all inputs before touching the database
- Return 400 for bad input, 401 for unauthenticated, 403 for unauthorized, 404 for not found
- Use a validation library (zod, joi, yup) for input schemas

## Error Handling
- Never expose internal error details to the client
- Log errors server-side with enough context to debug
- Propagate errors upward — do not silently swallow

## Do Not
- Put business logic in route handlers — use service functions
- Return different response shapes for different routes
- Expose database IDs directly if they reveal system internals

---
*Add real examples from your codebase as patterns solidify.*
