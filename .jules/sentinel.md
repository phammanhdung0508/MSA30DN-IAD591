# Sentinel Journal - Critical Security Learnings

## 2026-02-12 - Fix SQL Injection in Variable Time Intervals
**Vulnerability:** SQL Injection via f-string interpolation in SQLite `datetime` function parameters.
**Learning:** Even when input is expected to be an integer, using f-strings to build SQL queries is a dangerous pattern. In SQLite, parameterizing the interval in `datetime('now', '-24 hours')` requires concatenation or specific function calls because placeholders cannot be used inside string literals.
**Prevention:** Always use parameterized queries (`?`). For dynamic intervals in SQLite, use the concatenation operator: `datetime('now', '-' || ? || ' hours')`.
