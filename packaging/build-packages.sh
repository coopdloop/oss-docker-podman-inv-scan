#!/bin/bash
# Main script to build both RPM and DEB packages

set -e

# Change to script directory
cd "$(dirname "$0")"

echo "Building packages for container-inventory"
echo "----------------------------------------"

# Check if we should use Docker or native builds
if command -v docker &> /dev/null && [ -f "Dockerfile_rpm" ] && [ -f "Dockerfile_deb" ]; then
    echo "Using Docker-based builds..."
    if [ "$1" == "rpm" ]; then
        bash ./build-with-docker.sh rpm
    elif [ "$1" == "deb" ]; then
        bash ./build-with-docker.sh deb
    else
        bash ./build-with-docker.sh
    fi
else
    echo "Docker not available, using native builds..."
    # Create output directory
    OUTPUT_DIR="packages"
    mkdir -p ${OUTPUT_DIR}

    # Build RPM
    if [ "$1" != "deb" ]; then
        echo "Building RPM package..."
        cd scripts
        bash ./build-rpm.sh
        mv *.rpm ../${OUTPUT_DIR}/
        cd ..
    fi

    # Build DEB
    if [ "$1" != "rpm" ]; then
        echo "Building DEB package..."
        cd scripts
        bash ./build-deb.sh
        mv *.deb ../${OUTPUT_DIR}/
        cd ..
    fi

    echo "----------------------------------------"
    echo "Package building complete!"
    echo "Packages are available in the '${OUTPUT_DIR}' directory:"
    ls -la ${OUTPUT_DIR}
fi

echo "Done!"
