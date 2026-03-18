## 2026-03-18 - SQL Injection Pattern in SQLite Analytics Queries
**Vulnerability:** SQL injection via f-string interpolation in analytics functions (`get_sensor_summary`, `get_energy_analytics`, `get_temp_analytics`).
**Learning:** SQLite's `datetime` function with relative offsets (e.g., `'-24 hours'`) was being constructed using string interpolation. This is a common pitfall when the numeric value itself needs to be dynamic but the unit (hours/days) is fixed.
**Prevention:** Use standard SQL parameterization (`?`) and handle variable intervals using SQLite string concatenation: `datetime('now', '-' || ? || ' hours')`. This allows the dynamic value to be passed safely as a separate parameter.
