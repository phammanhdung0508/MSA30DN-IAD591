## 2026-04-10 - Parameterizing SQLite date intervals
**Vulnerability:** SQL injection via f-string interpolation of numeric intervals in `datetime()` functions.
**Learning:** Even when parameters are expected to be integers (like `hours` or `days`), direct interpolation into SQL strings remains dangerous. SQLite allows safe parameterization of these intervals using string concatenation within the SQL query (e.g., `'-' || ? || ' hours'`).
**Prevention:** Always use `?` placeholders for all external inputs in SQL queries, regardless of the expected data type.
