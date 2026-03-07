# Sentinel Journal 🛡️

## 2025-01-24 - Parameterizing Dynamic Intervals in SQLite
**Vulnerability:** SQL Injection via f-string interpolation in `datetime('now', '-{variable} units')`.
**Learning:** Even when variables are expected to be integers, interpolating them directly into SQL strings is dangerous. SQLite doesn't support parameters directly inside string literals for `datetime` offsets.
**Prevention:** Use SQLite's string concatenation operator `||` to combine the parameter with the required unit string, e.g., `datetime('now', '-' || ? || ' hours')`.

## 2025-01-24 - CORS Credential Security with Wildcard Origins
**Vulnerability:** Insecure CORS configuration where `allow_origins=["*"]` was combined with `allow_credentials=True`.
**Learning:** Modern browsers block requests that attempt to use credentials with a wildcard origin. This configuration also potentially allows any site to make authenticated requests if not properly restricted.
**Prevention:** Always set `allow_credentials=False` when using `allow_origins=["*"]`. In production, restrict `allow_origins` to specific trusted domains.
