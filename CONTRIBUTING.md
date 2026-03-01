# Contributing to reddit2text

Contributions are welcome. This file explains how to set up your environment and run linting before submitting a PR.

## Development setup

If you don't have [uv](https://docs.astral.sh/uv/) installed, `make` will install it for you (requires `curl`).

From the repo root, run:

```sh
make
```

This creates a virtual environment (`.venv`), installs the package in editable mode with dev dependencies (ruff, flake8, mypy), and copies `.env.example` to `.env` if you don’t have one. Then activate the venv and add your Reddit API credentials to `.env`:

```sh
source .venv/bin/activate   # Windows: .venv\Scripts\activate
# Edit .env with your Reddit app client_id, client_secret, user_agent
```

## Testing

Reddit posts and comments are live and mutable (scores, deletions, new comments), so tests do **not** hit the real API. Instead we use:

- **JSON fixtures** in `tests/fixtures/`: frozen snapshots of one or more threads (post + nested comments).
- **Fake PRAW objects**: in `tests/conftest.py`, fixture data is turned into objects that quack like `praw.models.Submission` and comment trees (`.author.name`, `.body`, `.score`, `.replies`, etc.).
- **Patching**: `Reddit2Text`’s PRAW instance is patched so `submission(url=...)` returns the fake submission built from the fixture.

This keeps tests fast, deterministic, and free of API credentials. Run tests with:

```sh
make test
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
