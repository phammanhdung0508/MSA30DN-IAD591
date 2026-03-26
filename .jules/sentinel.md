## 2025-05-22 - SQL Injection in SQLite datetime() functions
**Vulnerability:** String interpolation (f-strings) was used to inject user-provided `hours` and `days` parameters directly into SQLite `datetime('now', '-{hours} hours')` calls within `apps/api/database.py`.
**Learning:** Even when parameters are expected to be integers, they can be manipulated if passed as strings from the API layer. SQLite's `datetime()` function arguments are strings, making them susceptible to injection if not handled as bound parameters.
**Prevention:** Use the SQLite `||` string concatenation operator to combine bound placeholders with fixed strings inside the SQL query, e.g., `datetime('now', '-' || ? || ' hours')`. This ensures the input is treated as data, not as part of the SQL command.
