.PHONY: install test lint typecheck format monitoring-up monitoring-down api alerts clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src tests

format:
	ruff format src tests
	ruff check --fix src tests

monitoring-up:
	docker compose -f monitoring/docker-compose.monitoring.yml up -d

monitoring-down:
	docker compose -f monitoring/docker-compose.monitoring.yml down

api:
	PYTHONPATH=src uvicorn stream_forge_r5.api:app --port 9200 --reload

alerts:
	PYTHONPATH=src python scripts/generate_alert_rules.py

reports:
	PYTHONPATH=src python scripts/generate_reports.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
