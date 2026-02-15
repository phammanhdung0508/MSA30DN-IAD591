## 2026-02-15 - SQLite Parameterization for Time Intervals
**Vulnerability:** SQL Injection via f-string interpolation in `datetime()` functions.
**Learning:** SQLite's `datetime()` function requires specific concatenation when using parameters for interval values (e.g., `datetime('now', '-' || ? || ' hours')`). Direct interpolation of variables into the SQL string, even if validated elsewhere, bypasses the safety of parameterized queries.
**Prevention:** Always use the `||` operator to concatenate parameters within SQLite date/time functions instead of using f-strings or `.format()`.
