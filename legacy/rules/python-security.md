---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python Security

> Extends [common-security.md](./common-security.md).

- Read secrets from environment variables; never commit them.
- Run **bandit** for static security analysis: `bandit -r <package>/`.
