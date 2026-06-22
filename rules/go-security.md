---
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
---
# Go Security

> Extends [common-security.md](./common-security.md).

- **gosec** for static security analysis: `gosec ./...`
- **govulncheck** to scan dependencies for known CVEs: `govulncheck ./...`
