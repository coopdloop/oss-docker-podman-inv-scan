#!/bin/bash
set -e

# Configuration
PACKAGE_NAME="container-inventory"
VERSION=$(grep -oP "__version__ = \"\K[^\"]+" /source/container_inventory/__init__.py)
DEBIAN_DIR="/source/packaging/debian"
BUILD_DIR="/tmp/build-${PACKAGE_NAME}"

echo "Building DEB package for ${PACKAGE_NAME} version ${VERSION}"

# Create build directory
mkdir -p ${BUILD_DIR}

# Create original tarball (required by Debian tools)
echo "Creating original tarball..."
cd /source
tar --exclude='.git' --exclude='packaging' -czf ${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}.orig.tar.gz .

# Create the package directory
echo "Setting up build directory..."
mkdir -p ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}
# Extract the tarball to get a clean source tree
tar -xzf ${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}.orig.tar.gz -C ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}

# Create the debian directory
echo "Setting up debian directory..."
mkdir -p ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian
cp -r ${DEBIAN_DIR}/* ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/
# Make sure rules file is executable
chmod +x ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/rules
# Remove compat file as we use debhelper-compat dependency in control file
rm -f ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/compat

# Build DEB
echo "Building DEB package..."
cd ${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}
# Use -us -uc to skip signing and -d to skip lintian checks
debuild -us -uc -d

# Copy the built DEBs to output directory
echo "Copying DEBs to output directory..."
mkdir -p /output
cp ${BUILD_DIR}/*.deb /output/
cp ${BUILD_DIR}/*.dsc /output/ || true
cp ${BUILD_DIR}/*.tar.* /output/ || true
cp ${BUILD_DIR}/*.changes /output/ || true

echo "DEB package build complete!"
echo "The following packages have been created:"
ls -la /output/*.deb

echo "Done!"
