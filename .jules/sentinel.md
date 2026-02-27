## 2026-02-12 - SQL Injection in SQLite Intervals
**Vulnerability:** SQL injection vulnerability via f-string interpolation in SQLite `datetime` function intervals (e.g., `datetime('now', '-{hours} hours')`).
**Learning:** SQLite does not allow direct parameterization of the entire interval string in `datetime()`. However, parameterization can be achieved by using the `||` concatenation operator to combine the constant parts of the interval with a placeholder for the variable part (e.g., `datetime('now', '-' || ? || ' hours')`).
**Prevention:** Avoid f-strings or string concatenation for any part of a SQL query. Use the `||` operator in SQLite to safely build dynamic strings within the query using standard `?` placeholders.
