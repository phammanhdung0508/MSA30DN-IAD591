## 2026-02-12 - SQLite Interval Parameterization Pattern
**Vulnerability:** SQL Injection via f-string interpolation of time intervals in SQLite `datetime` functions.
**Learning:** While standard parameters work for simple values, SQLite requires string concatenation (`||`) to parameterize intervals inside `datetime('now', ...)` calls if the unit or direction is also dynamic.
**Prevention:** Use the pattern `datetime('now', '-' || ? || ' hours')` to safely inject numeric values into interval strings.

## 2026-02-12 - FastAPI CORS Wildcard Constraint
**Vulnerability:** Insecure/Invalid CORS configuration using `allow_origins=["*"]` with `allow_credentials=True`.
**Learning:** FastAPI (via Starlette) prohibits this combination because browsers block credentialed requests to a wildcard origin. Setting `allow_credentials=True` while using `*` can lead to both security risks and broken functionality.
**Prevention:** Always set `allow_credentials=False` when using `allow_origins=["*"]`, or specify an explicit list of allowed origins.
