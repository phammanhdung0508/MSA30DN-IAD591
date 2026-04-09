## 2025-01-24 - SQL Injection in SQLite datetime() intervals
**Vulnerability:** SQL injection via f-string interpolation in SQLite `datetime()` function modifiers.
**Learning:** Using f-strings to build SQLite `datetime()` modifiers (e.g., `datetime('now', '-{hours} hours')`) allows attackers to escape the function call and inject arbitrary SQL if the input is not strictly validated as an integer.
**Prevention:** Use parameterized queries with SQLite string concatenation (`||`) to build the modifier string safely: `datetime('now', '-' || ? || ' hours')`.
