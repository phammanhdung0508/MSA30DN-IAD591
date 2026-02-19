## 2026-02-19 - Parameterized SQL Intervals in SQLite
**Vulnerability:** SQL injection via f-string interpolation in database queries using variable time intervals (e.g., `datetime('now', '-{hours} hours')`).
**Learning:** Even if the input is typed as an integer, using f-strings for query construction is a bad practice and can lead to vulnerabilities if types are bypassed or if the pattern is copied to other non-integer fields. Parameterizing intervals in SQLite requires using string concatenation within the SQL itself: `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Always use `?` placeholders for all dynamic values in SQL queries. For SQLite-specific functions like `datetime`, use the `||` concatenation operator to combine parameters with units.
