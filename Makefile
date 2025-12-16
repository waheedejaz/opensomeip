# SOME/IP Stack Makefile

.PHONY: all clean docs diagrams test build install

# Default target
all: build

# Build the project
build:
	@echo "Building SOME/IP stack..."
	mkdir -p build
	cd build && cmake .. && make

# Run tests
test: build
	@echo "Running tests..."
	cd build && ctest --output-on-failure

# Generate documentation and diagrams
docs: diagrams
	@echo "Generating documentation..."

# Generate PlantUML diagrams
diagrams:
	@echo "Generating PlantUML diagrams..."
	./tools/plantuml/generate_diagrams.sh

# Clean build artifacts and dependencies
clean:
	@echo "Cleaning build artifacts and dependencies..."
	./scripts/clean_build.sh

# Install the stack
install: build
	@echo "Installing SOME/IP stack..."
	cd build && make install

# Development setup
setup:
	@echo "Setting up development environment..."
	./scripts/setup.sh

# Safety testing
safety-test: build
	@echo "Running safety-critical tests..."
	cd build && ctest -L safety --output-on-failure

# Performance testing
perf-test: build
	@echo "Running performance tests..."
	./scripts/performance_test.sh

# Code formatting
format:
	@echo "Formatting code..."
	./scripts/format.sh

# Static analysis
analyze:
	@echo "Running static analysis..."
	./tools/static_analysis/run_analysis.sh

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build the entire project"
	@echo "  build        - Build the SOME/IP stack"
	@echo "  test         - Run all tests"
	@echo "  docs         - Generate documentation"
	@echo "  diagrams     - Generate PlantUML diagrams"
	@echo "  clean        - Clean build artifacts and cached dependencies"
	@echo "  install      - Install the stack"
	@echo "  setup        - Setup development environment"
	@echo "  safety-test  - Run safety-critical tests"
	@echo "  perf-test    - Run performance tests"
	@echo "  format       - Format code"
	@echo "  analyze      - Run static analysis"
	@echo "  help         - Show this help message"
