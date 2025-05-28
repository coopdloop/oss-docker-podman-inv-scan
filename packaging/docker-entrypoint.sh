#!/bin/bash
set -e

# Configuration
PACKAGE_NAME="container-inventory"
VERSION=$(grep -oP "__version__ = \"\K[^\"]+" /source/container_inventory/__init__.py)
SPEC_FILE="/source/packaging/rpm/${PACKAGE_NAME}.spec"
BUILD_DIR=~/rpmbuild

echo "Building RPM package for ${PACKAGE_NAME} version ${VERSION}"

# Create source tarball
echo "Creating source tarball..."
mkdir -p /tmp/build-source
cp -r /source /tmp/build-source/${PACKAGE_NAME}-${VERSION}
tar -czf ${BUILD_DIR}/SOURCES/${PACKAGE_NAME}-${VERSION}.tar.gz -C /tmp/build-source ${PACKAGE_NAME}-${VERSION}

# Copy spec file and additional sources
cp ${SPEC_FILE} ${BUILD_DIR}/SPECS/
cp /source/packaging/container-inventory.service ${BUILD_DIR}/SOURCES/
cp /source/packaging/container-inventory.timer ${BUILD_DIR}/SOURCES/

# Build RPM
echo "Building RPM..."
rpmbuild -ba ${BUILD_DIR}/SPECS/${PACKAGE_NAME}.spec

# Copy the built RPMs to output directory
echo "Copying RPMs to output directory..."
mkdir -p /output
cp ${BUILD_DIR}/RPMS/*/*.rpm /output/
cp ${BUILD_DIR}/SRPMS/*.rpm /output/

echo "RPM package build complete!"
echo "The following packages have been created:"
ls -la /output/*.rpm

echo "Done!"
