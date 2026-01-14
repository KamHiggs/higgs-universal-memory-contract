.PHONY: help install test clean run-umc run-genesis run-all

help:
	@echo "Higgs Universal Memory Contract - Make targets"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install Python dependencies"
	@echo "  make install-dev      Install with dev dependencies"
	@echo ""
	@echo "Run:"
	@echo "  make run-umc          Run UMC memory server (port 8000)"
	@echo "  make run-genesis      Run Genesis void simulation"
	@echo "  make run-all          Run full stack (UMC + PostgreSQL + n8n)"
	@echo ""
	@echo "Test:"
	@echo "  make test             Run tests (TODO: need to write tests)"
	@echo "  make test-n8n         Run n8n-mcp integration tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove __pycache__, build artifacts"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

run-umc:
	@echo "Starting UMC Memory Server..."
	@echo "Access at: http://localhost:8000"
	@echo "Docs at: http://localhost:8000/docs"
	cd middleware && uvicorn umc_memory_server:app --reload

run-genesis:
	@echo "Running Genesis Void Architecture simulation..."
	python3 genesis_void_architecture.py

run-all:
	@echo "Starting full stack with Docker Compose..."
	docker-compose up

test:
	@echo "ERROR: Tests not yet implemented for Python code"
	@echo "TODO: Create tests/ directory with pytest tests"
	@exit 1

test-n8n:
	@echo "Running n8n-mcp integration tests..."
	cd integrations/n8n-mcp && npm test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf dist/ build/ *.egg-info
