## 2025-05-15 - Configurable CORS Origins
**Vulnerability:** Overly permissive CORS configuration (`allow_origins=["*"]`) combined with `allow_credentials=True`.
**Learning:** Hardcoding `*` for CORS origins is a common development shortcut that often leaks into production, creating a CSRF-like risk when credentials (cookies/auth headers) are involved.
**Prevention:** Always use environment variables for CORS origins, provide a sensible default for development, and include server-side warnings when insecure configurations are active.
