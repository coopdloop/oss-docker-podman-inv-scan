#!/bin/bash
# Main script to build both RPM and DEB packages

set -e

# Change to script directory
cd "$(dirname "$0")"

# Create output directory
OUTPUT_DIR="packages"
mkdir -p ${OUTPUT_DIR}

echo "Building packages for container-inventory"
echo "----------------------------------------"

# Build RPM
echo "Building RPM package..."
cd scripts
bash ./build-rpm.sh
mv *.rpm ../${OUTPUT_DIR}/
cd ..

# Build DEB
echo "Building DEB package..."
cd scripts
bash ./build-deb.sh
mv *.deb ../${OUTPUT_DIR}/
cd ..

echo "----------------------------------------"
echo "Package building complete!"
echo "Packages are available in the '${OUTPUT_DIR}' directory:"
ls -la ${OUTPUT_DIR}

echo "Done!"
