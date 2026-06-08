UV := uv

.DEFAULT_GOAL := help

.PHONY: help install run lint fmt clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?##"}; {printf "%-10s %s\n", $$1, $$2}'

install: ## Install dependencies
	$(UV) sync

run: ## Run example.py (demonstrates the custom Jinja error handler)
	$(UV) run python example.py

lint: ## Check code with ruff
	$(UV) run ruff check .

fmt: ## Format code with ruff
	$(UV) run ruff format .

clean: ## Remove .venv and build artifacts
	rm -rf .venv dist __pycache__ .ruff_cache
