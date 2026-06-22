# Common Security

- Never hardcode secrets (API keys, passwords, tokens). Use environment variables or a secret manager, validate they exist at startup, and rotate anything that may have leaked.
- Don't trust external data (user input, API responses, file content) — validate it at system boundaries.
- Prevent injection: parameterized queries for SQL, escape/sanitize for XSS. Apply auth/authorization based on the sensitivity of each surface.
- Error messages must not leak sensitive data.
