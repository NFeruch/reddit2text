# Development targets (run from repo root).
.PHONY: all setup setup-clean clean lint test

all: setup

# clean: remove .venv and Python cache/build dirs.
clean:
	rm -rf .venv .mypy_cache build dist reddit2text.egg-info reddit2text/__pycache__ tests/__pycache__

# setup-clean: clean then setup (fresh .venv and reinstall deps).
setup-clean: clean
	$(MAKE) setup

# setup: one shell script; each step below runs in order in that same shell.
# 1. Install uv if not in PATH (curl | sh; installer puts binary in ~/.local/bin).
# 2. Prepend ~/.local/bin to PATH so we see uv right after install.
# 3. Unset VIRTUAL_ENV so uv uses this repo's .venv, not an already-activated venv.
# 4. uv sync: create .venv if missing, install project + [dev] deps from pyproject.toml.
# 5. If .env missing, copy .env.example to .env and print a reminder.
# 6. Print activation instructions and remind to add Reddit credentials to .env.
setup:
	@command -v uv >/dev/null 2>&1 || (curl -LsSf https://astral.sh/uv/install.sh | sh); \
	export PATH="$$HOME/.local/bin:$$PATH"; \
	unset VIRTUAL_ENV; \
	uv sync --extra dev; \
	if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example — add your Reddit API credentials there."; else echo ".env already exists."; fi; \
	echo ""; echo "Setup complete. Activate the environment with:"; echo "  source .venv/bin/activate   # macOS/Linux"; echo "  .venv\\Scripts\\activate     # Windows"; echo ""; echo "Then add your Reddit app credentials to .env (see .env.example)."

# lint: style, format, and type checks (run before submitting a PR).
lint:
	.venv/bin/ruff check --fix .   # Lint and auto-fix
	.venv/bin/ruff format .       # Format to line length 79, double quotes
	.venv/bin/flake8 .            # Extra style checks (.flake8)
	.venv/bin/mypy reddit2text    # Type check (pyproject.toml)

# test: run pytest against tests/ using fixtures only (no live API).
test:
	.venv/bin/pytest tests/ -v
