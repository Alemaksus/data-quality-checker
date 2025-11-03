.PHONY: help test test-cov test-unit test-integration install clean run

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make run           - Start API server"
	@echo "  make clean         - Clean temporary files"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

run:
	uvicorn src.api.main:app --reload

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf logs/htmlcov
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf reports/*.html reports/*.md reports/*.pdf
	rm -rf tmp/*

