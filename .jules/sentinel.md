## 2026-04-08 - Parameterizing Time Intervals in SQLite
**Vulnerability:** SQL Injection via f-string interpolation in `datetime()` and `strftime()` functions within SQLite queries.
**Learning:** Even when the primary query parameters (like `device_id`) are sanitized, dynamic values used inside SQLite date/time functions (like `hours` or `days` in `datetime('now', '-{hours} hours')`) can be entry points for SQL injection if not properly parameterized.
**Prevention:** Use SQLite's string concatenation operator `||` to combine a placeholder with the interval unit, e.g., `datetime('now', '-' || ? || ' hours')`, allowing the interval value to be safely passed as a parameter.
