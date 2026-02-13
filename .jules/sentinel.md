## 2026-02-13 - SQL Injection in Variable Time Intervals
**Vulnerability:** SQL injection via f-string interpolation of interval values (hours, days) in SQLite `datetime()` function calls.
**Learning:** Even when input is validated as an integer in the API layer, using f-strings for SQL queries violates the principle of separation of code and data and can be bypassed if the function is reused elsewhere.
**Prevention:** Always use parameterized queries (`?` placeholders). For SQLite `datetime` intervals, use string concatenation within the SQL: `datetime('now', '-' || ? || ' hours')`.
