#!/bin/bash
# Script to build RPM package for container-inventory

set -e

# Configuration
PACKAGE_NAME="container-inventory"
VERSION=$(grep -oP "__version__ = \"\K[^\"]+" ../../container_inventory/__init__.py)
SPEC_FILE="../rpm/${PACKAGE_NAME}.spec"
BUILD_DIR=$(pwd)/rpmbuild
SOURCE_DIR=$(cd ../../ && pwd)

# Make sure rpmbuild is installed
if ! command -v rpmbuild &> /dev/null; then
    echo "Error: rpmbuild is not installed. Please install the rpm-build package."
    exit 1
fi

echo "Building RPM package for ${PACKAGE_NAME} version ${VERSION}"

# Create build directories
mkdir -p ${BUILD_DIR}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source tarball
echo "Creating source tarball..."
(cd ${SOURCE_DIR}/.. && tar -czf ${BUILD_DIR}/SOURCES/${PACKAGE_NAME}-${VERSION}.tar.gz --transform "s/^${PACKAGE_NAME}/${PACKAGE_NAME}-${VERSION}/" ${PACKAGE_NAME})

# Copy spec file
cp ${SPEC_FILE} ${BUILD_DIR}/SPECS/

# Build RPM
echo "Building RPM..."
rpmbuild --define "_topdir ${BUILD_DIR}" -ba ${BUILD_DIR}/SPECS/${PACKAGE_NAME}.spec

# Copy the built RPMs to current directory
echo "Copying RPMs to current directory..."
find ${BUILD_DIR}/RPMS -name "*.rpm" -exec cp {} . \;
find ${BUILD_DIR}/SRPMS -name "*.rpm" -exec cp {} . \;

echo "RPM package build complete!"
echo "The following packages have been created:"
ls -la *.rpm

# Cleanup
echo "Cleaning up build directory..."
rm -rf ${BUILD_DIR}

echo "Done!"
