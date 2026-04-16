# Database Patterns Reference — LoreForge

Load this file when working with the database, writing queries, or creating migrations.

## Stack
- Database: PostgreSQL
- ORM / Query builder: SQLAlchemy
- Migration tool: specify your migration tool

## Migration Rules
- Every schema change requires a migration file — never edit the DB directly
- Migration naming: `YYYYMMDD_HHMMSS_description.sql` or follow ORM conventions
- Always test both `up` and `down` migrations
- Run: ``

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
