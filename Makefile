.PHONY: all setup lint

all: setup

setup:
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]"
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example — add your Reddit API credentials there."; else echo ".env already exists."; fi
	@echo ""; echo "Setup complete. Activate the environment with:"; echo "  source venv/bin/activate   # macOS/Linux"; echo "  venv\\Scripts\\activate     # Windows"; echo ""; echo "Then add your Reddit app credentials to .env (see .env.example)."

lint:
	venv/bin/ruff check --fix .
	venv/bin/ruff format .
	venv/bin/flake8 .
	venv/bin/mypy reddit2text
