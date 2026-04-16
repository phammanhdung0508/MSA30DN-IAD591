## 2026-04-16 - SQL Injection in Analytics Intervals
**Vulnerability:** SQL Injection in `get_sensor_summary`, `get_energy_analytics`, and `get_temp_analytics`.
**Learning:** SQLite intervals in `datetime()` or `strftime()` cannot be directly parameterized as a single string (e.g., `? hours`). Instead, they must be constructed using SQL string concatenation.
**Prevention:** Use the `||` operator to safely concatenate the bound parameter with the interval unit: `datetime('now', '-' || ? || ' hours')`.
