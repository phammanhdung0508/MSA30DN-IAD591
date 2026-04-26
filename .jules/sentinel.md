## 2026-04-25 - SQL Injection in Analytics Functions
**Vulnerability:** SQL injection in `get_sensor_summary`, `get_energy_analytics`, and `get_temp_analytics` via f-string interpolation of time intervals.
**Learning:** Even with API-level validation, direct string interpolation in SQL queries is a high risk. SQLite's `datetime()` function needs care when parameterizing intervals.
**Prevention:** Always use parameterized queries. Use SQLite's string concatenation (`||`) to safely combine placeholders with units (e.g., `'-' || ? || ' hours'`).
