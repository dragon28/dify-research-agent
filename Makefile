.PHONY: setup test lint report searx-check
setup: ; uv sync
test: ; uv run pytest -q
lint: ; uv run ruff check .
searx-check: ; curl -fsS "http://localhost:8080/search?q=test&format=json" | head -c 300
report: ; set -a; . ./.env; set +a; uv run python scripts/run_report.py "$(TOPIC)"
dsl: ; uv run python scripts/build_dsl.py
