## 2026-04-22 - SQL Injection in Analytics Endpoints
**Vulnerability:** SQL Injection in `get_sensor_summary`, `get_energy_analytics`, and `get_temp_analytics` within `apps/api/database.py`.
**Learning:** Using f-strings to inject parameters into SQLite's `datetime('now', ...)` function bypasses standard parameterization and allows arbitrary SQL execution if the input is not strictly validated as an integer.
**Prevention:** Always use `?` placeholders for user-supplied values, even when they are part of a function argument. Use SQLite string concatenation (`||`) to safely build time interval strings.
