## 2025-05-14 - SQL Injection in SQLite Time Modifiers

**Vulnerability:** User-controlled values were interpolated into SQLite `datetime()` functions using f-strings (e.g., `datetime('now', '-{hours} hours')`).
**Learning:** Even when variables are expected to be integers, interpolating them into SQL strings bypasses database-level protections and can be exploited if input validation is missing or bypassed at the application layer. SQLite doesn't allow direct parameterization of the full modifier string, but does allow concatenation within SQL.
**Prevention:** Use SQLite's concatenation operator `||` to combine parameters with fixed strings inside SQL functions, e.g., `datetime('now', '-' || ? || ' hours')`.
