## 2026-04-25 - SQL Injection in Analytics Functions

**Vulnerability:** SQL injection via f-strings in `get_sensor_summary`, `get_energy_analytics`, and `get_temp_analytics`. The `hours` and `days` parameters were interpolated directly into the SQL query.
**Learning:** Even if a parameter is expected to be an integer, if it's passed as part of an f-string in an API endpoint without strict type enforcement or sanitization, it can be exploited. FastAPI does some validation but defense in depth requires parameterized queries.
**Prevention:** Always use parameterized queries (`?` or `:name`) for all variable parts of a SQL statement, including those used in functions like `datetime()`.
