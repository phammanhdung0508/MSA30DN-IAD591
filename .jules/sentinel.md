# Sentinel Journal

## 2025-05-14 - SQL Injection in SQLite datetime intervals
**Vulnerability:** SQL injection via dynamic time intervals (hours/days) in SQLite `datetime()` and `strftime()` functions.
**Learning:** Even with type hinting (e.g., `hours: int`), if the input is interpolated into the SQL string via f-strings, it remains vulnerable to injection if validation is bypassed or if the data is coerced from a malicious string in an API layer.
**Prevention:** Always use parameterized queries (`?`). For dynamic intervals in SQLite, use string concatenation with the parameter: `datetime('now', '-' || ? || ' hours')`.
