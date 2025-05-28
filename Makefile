# Container Inventory - Package Management System

.PHONY: help install build test clean docker-build docker-test package package-rpm package-deb install-packages test-systemd demo all

# Default target
help:
	@echo "Container Inventory"
	@echo "=================="
	@echo ""
	@echo "Development (macOS):"
	@echo "  make demo              - Complete dev/test pipeline"
	@echo "  make install           - Setup development environment"
	@echo "  make test              - Run all tests"
	@echo "  make docker-test       - Test packaging in Docker"
	@echo ""
	@echo "Linux Production:"
	@echo "  make package           - Build RPM/DEB packages"
	@echo "  sudo make install-packages - Install packages"
	@echo "  make test-systemd      - Test systemd integration"
	@echo ""
	@echo "Custom Scripts:"
	@echo "  make YOUR_SCRIPT=script.py install-script"

# Development setup
install:
	@echo "Setting up development environment..."
	python3 -m pip install --upgrade pip
	python3 -m pip install pytest
	@echo "✅ Development environment ready"

# Build Python package (simplified - just check syntax)
build:
	@echo "Validating Python package..."
	python3 -m py_compile container_inventory/*.py
	python3 -m py_compile tests/*.py
	@echo "✅ Python syntax validation completed"

# Run tests
test:
	@echo "Running test suite..."
	python3 -m pytest tests/ -v
	@echo "✅ Tests completed"

# Clean artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf packaging/packages/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Docker build for testing
docker-build:
	@echo "Building Docker test environment..."
	./build-test-image.sh
	@echo "✅ Docker test image built"

# Run tests in Docker
docker-test: docker-build
	@echo "Running tests in Docker container..."
	./run-test-container.sh
	@echo "✅ Docker tests completed"

# Build packages using Docker
package: package-rpm package-deb

package-rpm:
	@echo "Building RPM package..."
	cd packaging && ./build-packages.sh rpm
	@echo "✅ RPM package built in packaging/packages/"

package-deb:
	@echo "Building DEB package..."
	cd packaging && ./build-packages.sh deb
	@echo "✅ DEB package built in packaging/packages/"

# Install packages on system (requires sudo)
install-packages:
	@echo "Installing packages on system..."
	@if [ -f packaging/packages/*.rpm ]; then \
		echo "Installing RPM package..."; \
		sudo rpm -ivh packaging/packages/*.rpm || sudo dnf install -y packaging/packages/*.rpm; \
	elif [ -f packaging/packages/*.deb ]; then \
		echo "Installing DEB package..."; \
		sudo dpkg -i packaging/packages/*.deb || sudo apt-get install -f; \
	else \
		echo "❌ No packages found. Run 'make package' first."; \
		exit 1; \
	fi
	@echo "✅ Package installed"

# Test systemd integration
test-systemd: install-packages
	@echo "Testing systemd timer and service..."
	@echo "Starting systemd timer..."
	sudo systemctl enable container-inventory.timer
	sudo systemctl start container-inventory.timer
	@echo "Timer status:"
	systemctl status container-inventory.timer --no-pager
	@echo ""
	@echo "Triggering manual run..."
	sudo systemctl start container-inventory.service
	@echo "Service status:"
	systemctl status container-inventory.service --no-pager
	@echo "✅ Systemd integration tested"

# Show systemd logs
show-logs:
	@echo "Container Inventory Service Logs:"
	@echo "================================="
	journalctl -u container-inventory.service --no-pager -n 50
	@echo ""
	@echo "Container Inventory Timer Logs:"
	@echo "==============================="
	journalctl -u container-inventory.timer --no-pager -n 20

# Custom script integration
install-script:
	@if [ -z "$(YOUR_SCRIPT)" ]; then \
		echo "❌ Usage: make YOUR_SCRIPT=path/to/script.py install-script"; \
		exit 1; \
	fi
	@echo "Installing custom script: $(YOUR_SCRIPT)"
	@mkdir -p container_inventory/custom
	@cp "$(YOUR_SCRIPT)" container_inventory/custom/custom_script.py
	@echo "✅ Custom script installed in container_inventory/custom/"

test-script: install-script
	@echo "Testing custom script integration..."
	@python -c "from container_inventory.custom.custom_script import *; print('✅ Custom script imports successfully')" || \
		echo "⚠️  Custom script may need adjustment for import compatibility"

# Complete demonstration pipeline
demo: clean install build test docker-test
	@echo ""
	@echo "🎉 DEMONSTRATION COMPLETE"
	@echo "========================"
	@echo "✅ Development environment installed"
	@echo "✅ Python syntax validated and tested"
	@echo "✅ Docker build and test environment verified"
	@echo ""
	@echo "For package building (Linux):"
	@echo "  make package"
	@echo ""
	@echo "For production deployment on Linux:"
	@echo "  sudo make install-packages"
	@echo "  make test-systemd"
