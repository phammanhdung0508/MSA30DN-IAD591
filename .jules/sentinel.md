## 2025-02-12 - [SQL Injection in SQLite Interval Functions]
**Vulnerability:** SQL injection via f-string interpolation into SQLite `datetime` and `strftime` functions.
**Learning:** Even when a variable (like `hours` or `days`) is intended to be an integer, using f-strings to inject it into SQL queries creates a vulnerability. Parameterizing these within SQLite function calls requires careful use of the `||` concatenation operator.
**Prevention:** Always use parameterized queries (`?`) and use SQLite's `||` operator to safely incorporate parameters into interval strings, e.g., `datetime('now', '-' || ? || ' hours')`.
