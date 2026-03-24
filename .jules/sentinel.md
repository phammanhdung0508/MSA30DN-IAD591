# Sentinel Journal - Critical Security Learnings

## 2025-05-14 - SQL Injection via Time Interval Parameters
**Vulnerability:** SQL Injection in `apps/api/database.py`. The `hours` and `days` parameters were interpolated into the query using f-strings, allowing arbitrary SQL to be executed via the `datetime()` function's interval string.
**Learning:** Even parameters intended to be simple integers can be vectors for SQL injection if interpolated directly into string literals within a query. SQLite's `datetime('now', '-' || ? || ' hours')` pattern provides a safe way to parameterize these values.
**Prevention:** Never use f-strings or string concatenation to build SQL queries with user-provided variables. Always use parameterized queries (with `?` or named placeholders) provided by the database driver.
