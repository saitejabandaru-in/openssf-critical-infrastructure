.PHONY: help install run test docker-build docker-up lint clean

help:
	@echo "OpenSSF Criticality Platform - Developer Commands:"
	@echo "  make install       Install python dependencies"
	@echo "  make run           Run local FastAPI dev server"
	@echo "  make test          Run pytest suite"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start stack using Docker Compose"
	@echo "  make lint          Check python syntax and types"

install:
	pip install -r backend/requirements.txt

run:
	PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --port 8000

test:
	PYTHONPATH=. python3 -m pytest tests/

docker-build:
	docker build -t openssf-criticality-platform:latest .

docker-up:
	docker-compose up -d --build

lint:
	python3 -m ruff check backend/ tests/ || true

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
