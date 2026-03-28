## 2025-05-14 - SQL Injection in SQLite datetime functions
**Vulnerability:** Use of Python f-strings to inject the 'hours' and 'days' parameters into SQLite 'datetime' functions in 'apps/api/database.py'.
**Learning:** Even for seemingly safe integer-like parameters, using string interpolation for SQL queries creates an injection vector if the input isn't strictly validated or typed at the boundary. SQLite's 'datetime' function expects its second argument as a specific string format (e.g., '-24 hours'), making parameterization slightly more complex than simple value substitution.
**Prevention:** Always use parameterized queries ('?') and leverage SQL concatenation ('||') to safely combine parameters with string literals for functions like 'datetime'.
