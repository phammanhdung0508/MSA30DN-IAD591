## 2026-04-25 - SQL Injection in Analytics Functions
**Vulnerability:** SQL injection via f-strings in SQLite `datetime()` function calls.
**Learning:** Even with type hinting (e.g., `hours: int`), using f-strings for SQL query construction is dangerous. If the function is called from elsewhere without type checking or if a malicious string is passed, it leads to SQL injection. SQLite's `datetime()` doesn't allow standard parameterization for the interval string (e.g., `'? hours'`), requiring safe string concatenation within the SQL itself.
**Prevention:** Always use parameterized queries (`?` placeholders). For dynamic intervals in SQLite, use `||` concatenation like `datetime('now', '-' || ? || ' hours')`.
