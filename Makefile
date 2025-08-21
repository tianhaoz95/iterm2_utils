.PHONY: test test-verbose test-ssh test-session test-multi-node test-all clean install install-dev help

help:
	@echo "Available commands:"
	@echo "  test              - Run all tests"
	@echo "  test-verbose      - Run tests with verbose output"
	@echo "  test-ssh          - Run SSH connection tests only"
	@echo "  test-session      - Run session management tests only"
	@echo "  test-multi-node   - Run multi-node initialization tests only"
	@echo "  test-all          - Run all tests with detailed coverage"
	@echo "  clean             - Clean build artifacts and cache"
	@echo "  install           - Install the package"
	@echo "  install-dev       - Install package with development dependencies"
	@echo "  help              - Show this help message"

test:
	python3 -m pytest tests/

test-verbose:
	python3 -m pytest tests/ -v

test-ssh:
	python3 -m pytest tests/test_ssh_connections.py -v

test-session:
	python3 -m pytest tests/test_session_management.py -v

test-multi-node:
	python3 -m pytest tests/test_multi_node_init.py -v

test-all:
	python3 -m pytest tests/ -v --tb=long

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install .

install-dev:
	pip install -e .[test]
