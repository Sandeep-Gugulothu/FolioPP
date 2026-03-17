.PHONY: help install dev up down build test deploy clean

help:
	@echo "ET Intelligence Platform Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Run development environment"
	@echo "  make up         - Start all services (Docker)"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build production images"
	@echo "  make test       - Run tests"
	@echo "  make deploy     - Deploy to Kubernetes"
	@echo "  make clean      - Clean up resources"

install:
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

dev: up
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "Qdrant: http://localhost:6333"
	@echo "Neo4j: http://localhost:7474"
	@echo "MinIO: http://localhost:9001"
	@echo "Ray: http://localhost:8265"

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	sleep 5
	python scripts/seed_database.py

down:
	docker-compose down

build:
	docker-compose build

test:
	cd backend && pytest tests/
	cd frontend && npm test

clean:
	docker-compose down -v
