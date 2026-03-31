## 2026-03-31 - SQL Injection in SQLite date/time functions
**Vulnerability:** String interpolation (f-strings) used to pass dynamic intervals to SQLite `datetime('now', ...)` functions.
**Learning:** Even when inputs are expected to be integers, using string interpolation in SQL queries is a high-risk pattern. SQLite's `||` operator can be used within the query to safely concatenate parameters with fixed units (e.g., `'-' || ? || ' hours'`).
**Prevention:** Always use parameterized queries (?) and database-native string concatenation for dynamic values in SQL statements.
