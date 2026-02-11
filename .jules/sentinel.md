## 2026-02-11 - SQL Injection in time-based queries
**Vulnerability:** SQL injection via string interpolation in SQLite `datetime` functions.
**Learning:** Even if input is expected to be an integer (and validated as such by FastAPI), using f-strings to build SQL queries is a vulnerability if the data flows into a layer that doesn't re-validate or if the validation is bypassed.
**Prevention:** Always use parameterized queries (`?`) and SQLite's string concatenation operator (`||`) to build dynamic time intervals safely: `datetime('now', '-' || ? || ' hours')`.
