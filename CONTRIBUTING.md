# Commit Convention

Professional engineering requires a standardized, clear, and actionable commit history. This project follows the **Conventional Commits** specification.

## 1. Commit Message Structure

Each commit consists of a **type**, an optional **scope**, and a **subject**.

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 1.1 Types
- **feat**: A new feature (correlates with `MINOR` in SemVer).
- **fix**: A bug fix (correlates with `PATCH` in SemVer).
- **docs**: Documentation changes only.
- **style**: Changes that do not affect the meaning of the code (formatting, semi-colons, etc.).
- **refactor**: A code change that neither fixes a bug nor adds a feature.
- **perf**: A code change that improves performance.
- **test**: Adding missing tests or correcting existing tests.
- **build**: Changes that affect the build system or external dependencies.
- **ci**: Changes to CI configuration files and scripts.
- **chore**: Maintenance tasks (dependency updates, file moves).

### 1.2 Scopes
Common scopes used in this project:
- `infra`: Terraform, EKS, Karpenter changes.
- `ingestion`: Ray Data pipelines, scrapers.
- `compute`: Model serving, pattern engine.
- `agent`: LangGraph logic, state management.
- `api`: FastAPI endpoints.
- `web`: React frontend updates.

## 2. Best Practices

- **Atomic Commits**: Keep each commit focused on a single logical change.
- **Imperative Mood**: Use "add feature" instead of "added feature" or "adds feature".
- **No Workspace Bloat**: Do not commit secrets, environment variables, or large binary files (use `.gitignore`).
- **Referencing Issues**: Include "Closes #123" in the footer when applicable.

---
*Standardizing our history ensures high velocity and clear accountability for future investors and stakeholders.*
