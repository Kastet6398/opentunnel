.PHONY: help install test run dev clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

run: ## Run the application
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev: ## Run in development mode with auto-reload
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

validate: ## Validate project structure
	python3 validate_structure.py

generate-secret: ## Generate a secure secret key
	python3 generate_secret_key.py

init-db: ## Initialize database tables
	python3 -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"

docs: ## Generate API documentation
	python3 api_docs.py

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov

lint: ## Run linting
	flake8 app tests

format: ## Format code
	black app tests
	isort app tests

docker-build: ## Build Docker image
	docker build -t routetunnel .

docker-run: ## Run Docker container
	docker run -p 8000:8000 routetunnel