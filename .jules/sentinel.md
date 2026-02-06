# Sentinel's Journal

## 2025-05-14 - SQL Injection in Analytics Queries
**Vulnerability:** SQL injection vulnerability in `get_energy_analytics` and `get_temp_analytics` functions within `apps/api/database.py`. The `days` parameter was directly interpolated into the SQL string using f-strings.
**Learning:** Even when a variable is typed as an `int` in Python/FastAPI, directly interpolating it into a SQL query is a dangerous pattern that can lead to vulnerabilities if type hints are bypassed or if the codebase evolves.
**Prevention:** Always use parameterized queries (e.g., `?` in SQLite) for all variable inputs in SQL statements, regardless of their source or expected type.
