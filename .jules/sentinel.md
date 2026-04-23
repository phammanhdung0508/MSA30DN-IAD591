## 2026-04-22 - SQL Injection in SQLite datetime() intervals
**Vulnerability:** SQL Injection via f-strings in SQLite `datetime()` function calls. User-provided `hours` or `days` integers were interpolated directly into the query string.
**Learning:** SQLite's `datetime()` and `strftime()` functions are often used with relative intervals (e.g., `'-24 hours'`). Developers might mistakenly use f-strings to build these interval strings, creating an injection point even if the input is expected to be an integer.
**Prevention:** Always use parameterized queries. To build dynamic relative intervals in SQLite, use string concatenation within the SQL itself: `datetime('now', '-' || ? || ' hours')`.
