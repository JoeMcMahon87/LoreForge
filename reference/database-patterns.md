# Database Patterns Reference — LoreForge

Load this file when working with the database, writing queries, or creating migrations.

## Stack
- Database: PostgreSQL 16
- ORM: Django ORM (no SQLAlchemy)
- Migration tool: `python manage.py makemigrations` / `python manage.py migrate`

## Migration Rules
- Every schema change requires a migration file — never edit the DB directly
- Migration naming: Django auto-names migrations; keep generated names unless clarity demands a rename
- Always run `python manage.py makemigrations --check` in CI to catch uncommitted schema changes
- Run: `python manage.py migrate`

## Query Conventions
- Use parameterized queries / ORM methods — never string-interpolated SQL
- Keep queries in service files, not in route handlers
- For complex queries, add a comment explaining what it does and why

## Performance Rules
- Add indexes for any column used in WHERE, JOIN, or ORDER BY clauses
- Avoid N+1 queries — use eager loading or batch fetching
- Query only the columns you need — avoid `SELECT *` in production code

## Transactions
Use transactions for multi-table writes

---
*Add real schema diagrams and example queries as the data model stabilizes.*
