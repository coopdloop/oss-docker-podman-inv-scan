# Container Inventory Project

## What This Project Does

Container Inventory is a command-line tool for managing and securing container images. It has two primary functions:

1. Container Image Inventory: Lists all Docker and Podman container images on your system with details like size, creation date, etc.

2. Vulnerability Scanning: Scans these images for security vulnerabilities using Trivy (if installed)

The tool is designed to work across different Linux distributions by packaging it as both RPM (for RHEL, Fedora, CentOS) and DEB (for Debian, Ubuntu) formats.

## Project Structure and Components

### Core Components

1. Python Package (container_inventory/):

- core.py: The main functionality for inventory and scanning
- cli.py: Command-line interface for users
- __init__.py: Package initialization and version information


2. Entry Points: Makes the tool callable as commands:

- container-inventory: The main command to inventory/scan containers
- container-inventory-create-test-images: Helper command to create test images


3. Packaging System: Files to build distributable packages

- rpm/: Files for Red Hat-based systems
- debian/: Files for Debian-based systems
- Docker-based build system to ensure consistent builds



## Packaging Fundamentals

### Python Packaging Basics

1. setup.py: Describes your Python package:

- Name, version, author information
- Dependencies (libraries required)
- Entry points (commands)
- Package discovery

2. MANIFEST.in: Controls which files are included in the package:

- Includes LICENSE, README.md
- Includes examples
- Excludes tests


## RPM Packaging

RPM (Red Hat Package Manager) is used by Red Hat-based systems:

1. container-inventory.spec: The specification file that defines:

- Package metadata (name, version, summary)
- Dependencies (Requires, BuildRequires)
- Build process (%build, %install)
- What files to include (%files)
- System installation instructions


2. Build Process:

- Source code is packaged into a tarball
- RPM runs setup.py build and setup.py install
- Files are organized into a directory structure
- Package metadata is added
- Finally compiled into an .rpm file



## DEB Packaging

DEB is used by Debian-based systems like Ubuntu:

1. debian/ directory containing:

- control: Package metadata and dependencies
- changelog: Version history
- copyright: License information
- rules: Instructions for building the package (similar to a Makefile)
- source/format: Packaging format specification


2. Build Process:

- Source code is packaged into .orig.tar.gz
- debian/ directory is added
- debuild tool builds the package
- Results in .deb files


## Docker-Based Build System

We use Docker to create consistent build environments:

1. Why Docker:

- Ensures the same build environment regardless of host OS
- No need to install RPM/DEB tools on your system
- Reproducible builds across different machines


2. Dockerfile.rpm:

- Based on Fedora
- Installs RPM build tools
- Sets up a build user


3. Dockerfile.deb:

- Based on Ubuntu
- Installs Debian packaging tools
- Sets up a build user



## Key Files Explained

### Python Package Files

- setup.py: The main Python packaging file that defines how to install your code

```python
# Contains package metadata, dependencies, and entry points
setup(
    name="container-inventory",
    version="0.1.0",
    # ...
    entry_points={
        "console_scripts": [
            "container-inventory=container_inventory.cli:main",
        ],
    },
)
```

- container_inventory/core.py: The main functionality

```python
# Container image inventory and scanning
class ContainerInventory:
    # Methods to check Docker/Podman availability
    # Methods to list images
    # Methods to scan for vulnerabilities
```

## RPM Package Files
```
- rpm/container-inventory.spec: RPM build specification
# Package metadata
Name:           container-inventory
Version:        0.1.0
Release:        1%{?dist}

# Build requirements
BuildRequires:  python3-devel

# Installation sections
%install
%py3_install

# Files to include
%files
%license LICENSE
%{python3_sitelib}/container_inventory/
```

## DEB Package Files

- debian/control: Package metadata for Debian

```
Source: container-inventory
Maintainer: Your Name <your.email@example.com>

Package: container-inventory
Architecture: all
Depends: ${python3:Depends}, ${misc:Depends}
Description: Docker and Podman container image inventory and vulnerability scanner
```

- debian/rules: Build instructions

```
#!/usr/bin/make -f
export PYBUILD_NAME=container-inventory
%:
	dh $@ --with python3 --buildsystem=pybuild
```

## Docker Build Files

- build-with-docker.sh: Main build script

```
# Build RPM and DEB packages using Docker containers
docker build -t container-inventory-rpm-builder -f Dockerfile.rpm .
docker run --rm \
    -v "$(cd .. && pwd):/source" \
    -v "$(pwd)/${OUTPUT_DIR}:/output" \
    container-inventory-rpm-builder
```


## Build Process Walkthrough

When you run ./packaging/build-with-docker.sh, the following happens:

1. Docker Container Creation:

- Builds Docker images for RPM and DEB packaging
- Sets up build environments with necessary tools


2. For RPM Build:

- Source code is copied into the container
- The spec file is used to guide the build
- Python package is built and installed within the container
- Files are organized into a structure
- RPM file is created in the packages/ directory


3. For DEB Build:

- Source code is packaged into an original tarball
- Debian directory is added to the source
- debuild tool creates the package
- DEB file is saved to the packages/ directory

## Why This Approach?

This approach was chosen for several reasons:

1. Cross-platform compatibility: Users can install on different Linux distributions
2. Easy distribution: System package managers (dnf, apt) can handle installation
3. Dependencies management: Package systems handle dependencies automatically
4. System integration: Tools appear in PATH and are properly registered
5. Updates management: Package systems can handle updates

## Common Issues and Solutions

1. Build Environment Problems:

- Docker fixes most of these by providing consistent environments


2. Path Mismatches:

- RPM and DEB have different conventions for where files go
- Spec file and debian/control handle these differences


3. Test Files in Packages:

- Tests shouldn't be in the final package
- We exclude them in setup.py and manually remove them


4. Version Management:

- Version is maintained in one place (__init__.py) and extracted for packaging



## Using the Packaged Tool

After building and installing the package:

```
# Inventory all containers
container-inventory

# Scan for vulnerabilities
container-inventory --scan

# Save results
container-inventory --output inventory.json
```
