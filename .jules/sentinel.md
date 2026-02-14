## 2026-02-14 - SQL Injection in SQLite datetime functions
**Vulnerability:** SQL injection vulnerability in `apps/api/database.py` where user-provided (or potentially user-controlled) `hours` and `days` values were interpolated into SQL queries using f-strings.
**Learning:** Even when inputs are typed as integers in FastAPI, it is critical to use parameterized queries to prevent SQL injection at the database layer. In SQLite, parameterized intervals in `datetime` functions can be achieved using the concatenation operator `||`.
**Prevention:** Always use `?` placeholders for all variable parts of an SQL query. Avoid using f-strings or string concatenation for building SQL queries, even for values that are expected to be numeric.
