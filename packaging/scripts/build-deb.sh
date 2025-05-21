#!/bin/bash
# Script to build DEB package for container-inventory

set -e

# Configuration
PACKAGE_NAME="container-inventory"
VERSION=$(grep -oP "__version__ = \"\K[^\"]+" ../../container_inventory/__init__.py)
SOURCE_DIR=$(cd ../../ && pwd)
BUILD_DIR=$(pwd)/debbuild
DEBIAN_DIR="../debian"

# Make sure required tools are installed
if ! command -v debuild &> /dev/null; then
    echo "Error: debuild is not installed. Please install the devscripts and debhelper packages."
    exit 1
fi

echo "Building DEB package for ${PACKAGE_NAME} version ${VERSION}"

# Create build directory
mkdir -p ${BUILD_DIR}
rm -rf ${BUILD_DIR}/*

# Create a copy of the source
echo "Creating source copy..."
cp -r ${SOURCE_DIR} ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}

# Create the debian directory
echo "Setting up debian directory..."
mkdir -p ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian
cp -r ${DEBIAN_DIR}/* ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/

# Build DEB
echo "Building DEB package..."
(cd ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION} && debuild -us -uc)

# Copy the built DEBs to current directory
echo "Copying DEBs to current directory..."
find ${BUILD_DIR} -name "*.deb" -exec cp {} . \;
find ${BUILD_DIR} -name "*.dsc" -exec cp {} . \;
find ${BUILD_DIR} -name "*.tar.gz" -exec cp {} . \;
find ${BUILD_DIR} -name "*.changes" -exec cp {} . \;

echo "DEB package build complete!"
echo "The following packages have been created:"
ls -la *.deb

# Cleanup
echo "Cleaning up build directory..."
rm -rf ${BUILD_DIR}

echo "Done!"
