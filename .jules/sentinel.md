## 2026-04-01 - Parameterizing SQLite Time Intervals
**Vulnerability:** SQL injection via f-strings when building `datetime()` offsets in SQLite.
**Learning:** Standard parameterization `?` cannot be used directly inside a SQL string literal like `'-{hours} hours'`.
**Prevention:** Use SQLite string concatenation `||` to combine the placeholder with the unit: `datetime('now', '-' || ? || ' hours')`.
