## 2026-02-12 - [HIGH] SQL Injection in temporal intervals
**Vulnerability:** Several database functions (`get_sensor_summary`, `get_energy_analytics`, `get_temp_analytics`) were using f-string interpolation for time intervals (e.g., `{hours} hours`), creating a potential SQL injection path if the parameters were not strictly validated at the API layer.
**Learning:** Even with API validation, using string interpolation for SQL queries is a dangerous pattern. In SQLite, temporal intervals can be parameterized using string concatenation within the query: `datetime('now', '-' || ? || ' hours')`.
**Prevention:** Always use parameterized queries for all dynamic values, including intervals. Avoid f-strings in SQL execution entirely.
