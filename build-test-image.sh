#!/bin/bash
# Script to build the container-inventory test image

set -e

echo "Building Container Inventory Test Image..."
echo "=========================================="

# Build the Docker image
docker build -f Dockerfile.test -t container-inventory-test .

echo ""
echo "Build complete!"
echo ""
echo "To run the test container:"
echo "  ./run-test-container.sh"
echo ""
echo "To run interactively:"
echo "  ./run-test-container.sh --interactive"
