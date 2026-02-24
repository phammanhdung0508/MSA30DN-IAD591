## 2026-02-12 - Parameterizing SQLite Time Intervals
**Vulnerability:** SQL injection via f-string interpolation in SQLite `datetime` functions.
**Learning:** SQLite's `datetime` and `strftime` functions often take interval strings like `'-24 hours'`. When these intervals are dynamic, developers often use f-strings (`f"'-{hours} hours'"`), which is vulnerable.
**Prevention:** Use SQLite's string concatenation operator `||` to safely combine placeholders with literal strings: `datetime('now', '-' || ? || ' hours')`.
