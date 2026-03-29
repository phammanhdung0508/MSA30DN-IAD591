# Sentinel Journal

## 2025-05-22 - SQL Injection via Time Intervals in SQLite
**Vulnerability:** SQL injection was possible in `get_sensor_summary`, `get_energy_analytics`, and `get_temp_analytics` because the `hours` and `days` parameters were interpolated directly into the SQL string using f-strings.
**Learning:** Even simple numeric parameters can be dangerous if they are not validated or parameterized. SQLite's `datetime()` function can be parameterized by using string concatenation for the interval (e.g., `'-' || ? || ' hours'`).
**Prevention:** Always use parameterized queries for all user-supplied or dynamic inputs in SQL statements. Avoid f-string or manual string interpolation for SQL queries.
