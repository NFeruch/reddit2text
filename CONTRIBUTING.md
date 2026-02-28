# Contributing to reddit2text

Contributions are welcome. This file explains how to set up your environment and run linting before submitting a PR.

## Development setup

From the repo root, run:

```sh
make
```

This creates a virtual environment, installs the package in editable mode with dev dependencies (ruff, flake8, mypy), and copies `.env.example` to `.env` if you don’t have one. Then activate the venv and add your Reddit API credentials to `.env`:

```sh
source venv/bin/activate   # Windows: venv\Scripts\activate
# Edit .env with your Reddit app client_id, client_secret, user_agent
```

## Linting

Before submitting a PR, run:

```sh
make lint
```

- **Ruff**: auto-fix style and format (line length 79).
- **Flake8**: style checks (config in `.flake8`).
- **Mypy**: type checking (config in `pyproject.toml`).

## Pull requests and issues

Open an issue for discussion or a pull request with your changes. Make sure the lint steps above pass.
