## 2026-04-04 - SQL Injection in SQLite Time Intervals and Insecure CORS

**Vulnerability:** Several database functions (`get_sensor_summary`, `get_energy_analytics`, `get_temp_analytics`) were using Python f-strings to inject user-provided time intervals (hours/days) directly into SQLite `datetime()` calls. Additionally, CORS was configured with `allow_origins=["*"]` while `allow_credentials=True` was enabled, which is a security risk.

**Learning:** Parameterizing time intervals in SQLite's `datetime('now', ...)` function requires specific syntax because the interval string itself cannot be a single parameter if it contains both the value and the unit (e.g., '-24 hours'). The safest way is to use string concatenation within SQL: `datetime('now', '-' || ? || ' hours')`.

**Prevention:** Always use parameterized queries for all user-provided inputs, even for numeric-like parameters like "hours" or "days". For CORS, ensure that allowed origins are configurable and avoid wildcards in production, especially when credentials are allowed.
