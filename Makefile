.PHONY: help install test run clean lint

# Use bash as the default shell
SHELL := /bin/bash

# Default target
help:
	@echo "Available targets:"
	@echo "  install   - Create virtual environment and install dependencies"
	@echo "  test      - Run pytest with coverage"
	@echo "  run       - Execute the main script"
	@echo "  lint      - Run linting and code style checks"
	@echo "  clean     - Remove virtual environment and cached files"

# Create virtual environment and install dependencies
install:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt

# Run tests with pytest
test:
	@echo "Running tests..."
	. venv/bin/activate && \
		PYTHONPATH=$(pwd) pytest tests/new_test_main.py

# Run the main script
run:
	@echo "Running main script..."
	. venv/bin/activate && \
		python -m src.main

# Lint the code
lint:
	@echo "Running code linting..."
	. venv/bin/activate && \
		pip install flake8 && \
		flake8 src/ tests/

# Clean up virtual environment and cached files
clean:
	@echo "Cleaning up..."
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete