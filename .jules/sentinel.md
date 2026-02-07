## 2025-05-14 - [CRITICAL] SQL Injection in Sensor Analytics
**Vulnerability:** SQL injection via f-string interpolation in `apps/api/database.py`. The time interval (hours/days) was directly interpolated into the SQL query string within the `datetime()` function.
**Learning:** Even with input validation at the API level (e.g., FastAPI's type hinting and range checks), direct interpolation in SQL queries is a violation of the "parameterized queries only" directive and can lead to exploitation if validation is bypassed or modified.
**Prevention:** Always use `?` placeholders for all variable parts of a query, including values passed to SQL functions like `datetime()`. Use SQLite's concatenation operator `||` if necessary to build interval strings within the database.
