# Language-Specific Conventions

Quick-reference for non-C# languages. C# conventions live in the project
layer's coding skill (declared in `shared/project-routing.md` when mounted).

## Python

- Use **ruff** for formatting, linting, and import sorting; defer to
  `pyproject.toml` when present.
- Add type annotations to public function signatures.
- Use **pytest** with `pytest.mark` for test categorization; coverage via
  `pytest --cov=<package> --cov-report=term-missing`.
- Run **bandit** for static security analysis: `bandit -r <package>/`.
- Read secrets from environment variables; never commit them.
- System has no bare `python`; use `uv run <entry-point>` (entry name from
  `pyproject.toml [project.scripts]`), or `uv run python script.py` for
  one-off scripts.

## Go

- Use standard `go test` with **table-driven tests**.
- Always run with `-race`: `go test -race ./...`
- Coverage: `go test -cover ./...`
- **gosec** for static security analysis: `gosec ./...`
- **govulncheck** for dependency CVE scanning: `govulncheck ./...`
