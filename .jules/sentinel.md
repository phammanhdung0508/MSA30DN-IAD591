## 2026-04-25 - SQL Injection in Analytics functions
**Vulnerability:** Several analytics functions in `apps/api/database.py` used f-strings to inject time interval parameters (hours/days) directly into SQLite queries, making them vulnerable to SQL injection.
**Learning:** Using f-strings in SQL queries is a common but dangerous pattern, even for numeric-looking parameters. SQLite doesn't support placeholders directly for interval units in `datetime()` functions, requiring safe string concatenation within the SQL itself.
**Prevention:** Always use parameterized queries (`?` placeholders). For dynamic intervals in SQLite, use the pattern `datetime('now', '-' || ? || ' hours')` to safely concatenate parameters within the database engine.
