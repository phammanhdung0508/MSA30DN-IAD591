## 2025-05-15 - [SQL Injection in SQLite DateTime Offsets]
**Vulnerability:** SQL injection was found in `apps/api/database.py` where `hours` and `days` parameters were interpolated into f-strings within `datetime('now', '-{hours} hours')`.
**Learning:** Even when inputs are validated at the API layer (e.g. `hours: int`), database helper functions should remain defensive by using parameterized queries to prevent injection if called from other contexts or if API validation is bypassed.
**Prevention:** Use SQLite's string concatenation operator `||` to safely join placeholders with interval units, e.g., `datetime('now', '-' || ? || ' hours')`.
