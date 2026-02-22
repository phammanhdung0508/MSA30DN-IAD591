## 2026-02-22 - SQL Injection in SQLite Time Intervals
**Vulnerability:** SQL injection via f-string interpolation of time intervals in SQLite `datetime()` function.
**Learning:** Even when variables are validated as integers at the API level, interpolating them into SQL strings remains a vulnerability. SQLite allows parameterization of function arguments by concatenating the parameter with other strings using the `||` operator.
**Prevention:** Use the pattern `datetime('now', '-' || ? || ' units')` to safely parameterize variable time intervals in SQLite queries.

## 2026-02-22 - Wildcard CORS with Credentials
**Vulnerability:** FastAPI configured with `allow_origins=["*"]` and `allow_credentials=True`.
**Learning:** Modern browsers block CORS requests where the origin is a wildcard but credentials (cookies/auth headers) are requested. This configuration is also insecure as it allows any site to make authenticated requests if credentials were actually supported.
**Prevention:** When using `allow_origins=["*"]`, always set `allow_credentials=False`. If credentials are required, specific allowed origins must be listed.
