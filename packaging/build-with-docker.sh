#!/bin/bash
# Script to build packages using Docker containers

set -e

# Change to script directory
cd "$(dirname "$0")"

# Create output directory
OUTPUT_DIR="packages"
mkdir -p ${OUTPUT_DIR}

echo "Building packages for container-inventory using Docker"
echo "----------------------------------------------------"

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed or not available in PATH"
        exit 1
    fi
}

# Build RPM package
build_rpm() {
    echo "Building RPM package using Docker..."

    # Build the Docker image
    docker build -t container-inventory-rpm-builder -f Dockerfile.rpm .

    # Run the container to build the RPM
    docker run --rm \
        -v "$(cd .. && pwd):/source" \
        -v "$(pwd)/${OUTPUT_DIR}:/output" \
        container-inventory-rpm-builder

    echo "RPM build complete!"
}

# Build DEB package
build_deb() {
    echo "Building DEB package using Docker..."

    # Build the Docker image
    docker build -t container-inventory-deb-builder -f Dockerfile.deb .

    # Run the container to build the DEB
    docker run --rm \
        -v "$(cd .. && pwd):/source" \
        -v "$(pwd)/${OUTPUT_DIR}:/output" \
        container-inventory-deb-builder

    echo "DEB build complete!"
}

# Main execution
check_docker

# Check command line arguments
if [ "$1" == "rpm" ]; then
    build_rpm
elif [ "$1" == "deb" ]; then
    build_deb
else
    # Build both by default
    build_rpm
    build_deb
fi

echo "----------------------------------------------------"
echo "Package building complete!"
echo "Packages are available in the '${OUTPUT_DIR}' directory:"
ls -la ${OUTPUT_DIR}

echo "Done!"
