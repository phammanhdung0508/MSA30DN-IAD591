## 2026-02-16 - [SQL Injection in SQLite Intervals]
**Vulnerability:** SQL injection via f-string interpolation in SQLite `datetime` and `strftime` functions for dynamic time intervals (e.g., `datetime('now', '-{hours} hours')`).
**Learning:** SQLite doesn't directly support `?` placeholders inside the second argument of `datetime`. However, it can be securely parameterized by using the SQLite concatenation operator `||` to build the interval string: `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Always use parameterized queries and string concatenation within SQL rather than Python f-strings or `.format()` for any variable inputs in database queries.
