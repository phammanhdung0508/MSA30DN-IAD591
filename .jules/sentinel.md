## 2026-04-12 - SQL Injection in SQLite datetime modifiers
**Vulnerability:** Several functions in `apps/api/database.py` were using f-strings to interpolate integer parameters (`hours`, `days`) directly into the `datetime()` function's modifier string in SQL queries.
**Learning:** Even though the parameters were intended to be integers (and validated as such by FastAPI), constructing SQL queries using string interpolation for parameters is a security risk. SQLite does not allow direct parameterization of the modifier string in `datetime('now', '-? hours')`.
**Prevention:** Use SQL string concatenation to safely combine the parameter with the rest of the modifier string, e.g., `datetime('now', '-' || ? || ' hours')`. This allows the variable part to be safely parameterized.
