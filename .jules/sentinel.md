# Sentinel Journal - Smart Home IoT System

## 2026-02-12 - Journal Initialized
**Vulnerability:** N/A
**Learning:** Initializing the security journal for the Smart Home IoT System.
**Prevention:** N/A

## 2026-02-16 - Parameterized Time Intervals in SQLite
**Vulnerability:** SQL Injection in dynamic time interval parameters.
**Learning:** Using f-strings to interpolate values into SQLite's `datetime` function (e.g., `datetime('now', '-{hours} hours')`) creates a SQL injection vulnerability even if the variables are expected to be integers.
**Prevention:** Use the SQLite concatenation operator `||` with parameterized placeholders: `datetime('now', '-' || ? || ' hours')`. This ensures the input is treated as a literal value rather than part of the SQL command.
