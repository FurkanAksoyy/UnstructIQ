.PHONY: help build up down logs clean restart

help:
	@echo "UnstructIQ - Docker Commands"
	@echo "============================"
	@echo "make build    - Build Docker images"
	@echo "make up       - Start services"
	@echo "make down     - Stop services"
	@echo "make logs     - View logs"
	@echo "make restart  - Restart services"
	@echo "make clean    - Clean up everything"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f