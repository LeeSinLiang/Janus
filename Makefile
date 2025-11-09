.PHONY: all install-backend install-frontend install run-backend run-frontend run init

all: init run

# Installation
install-backend:
	@echo "Installing backend dependencies..."
	pip install -r backend/requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend/janus && npm install

install: install-backend install-frontend

# Database migration
migrate:
	@echo "Running Django migrations..."
	cd backend/src && python manage.py migrate

# Initialization
init: install migrate

# Running the servers
run-backend:
	@echo "Starting backend server..."
	cd backend/src && python manage.py runserver

run-frontend:
	@echo "Starting frontend server..."
	cd frontend/janus && npm run dev

run: run-backend run-frontend
