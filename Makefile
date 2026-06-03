.PHONY: dev test test-cov lint format build clean

dev:
	pip install -e ".[dev,pandas]"

test:
	pytest -v

test-cov:
	pytest -v --cov=vn_market_calendar --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

build:
	python -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
