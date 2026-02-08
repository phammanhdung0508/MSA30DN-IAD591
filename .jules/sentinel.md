# Sentinel Journal - Critical Security Learnings

## 2025-05-14 - [SQL Injection in SQLite Time Intervals]
**Vulnerability:** String interpolation (f-strings) was used to inject variable time intervals (hours/days) into SQLite `datetime` functions.
**Learning:** Even if input is validated as an integer at the API level, the database layer should remain agnostic and use parameterized queries. SQLite doesn't allow direct parameterization of the interval string (e.g., `'-? hours'`).
**Prevention:** Use SQLite's concatenation operator `||` to build the interval string safely: `datetime('now', '-' || ? || ' hours')`.
