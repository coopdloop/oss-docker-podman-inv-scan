# Container-Inventory Installation Guide

This document provides instructions for installing the Container-Inventory tool from RPM and DEB packages.

## Prerequisites

### For all systems:
- Python 3.6 or higher

### For vulnerability scanning:
- [Trivy](https://github.com/aquasecurity/trivy) (optional)

### For container runtime:
- Docker and/or Podman

## Installing from RPM (RHEL, Fedora, CentOS)

1. Download the RPM package:
   ```bash
   curl -LO https://your-repo-url/path/to/container-inventory-0.1.0-1.noarch.rpm
   ```

2. Install the package:
   ```bash
   sudo dnf install container-inventory-0.1.0-1.noarch.rpm
   ```

   Or on older systems:
   ```bash
   sudo yum install container-inventory-0.1.0-1.noarch.rpm
   ```

3. Verify installation:
   ```bash
   container-inventory --help
   ```

## Installing from DEB (Debian, Ubuntu)

1. Download the DEB package:
   ```bash
   curl -LO https://your-repo-url/path/to/container-inventory_0.1.0-1_all.deb
   ```

2. Install the package:
   ```bash
   sudo apt install ./container-inventory_0.1.0-1_all.deb
   ```

3. Verify installation:
   ```bash
   container-inventory --help
   ```

## Configuration

Container-Inventory works out of the box without any configuration. However, for vulnerability scanning capabilities, you need to have Trivy installed:

### Installing Trivy

Follow the [official Trivy installation instructions](https://github.com/aquasecurity/trivy#installation).

For example, on Debian/Ubuntu:
```bash
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

For RHEL/CentOS:
```bash
sudo rpm -ivh https://github.com/aquasecurity/trivy/releases/download/v0.36.1/trivy_0.36.1_Linux-64bit.rpm
```

## Usage

Basic usage:
```bash
# List all container images
container-inventory

# Scan for vulnerabilities
container-inventory --scan

# Save inventory to a file
container-inventory --output inventory.json
```

For more options, see the help:
```bash
container-inventory --help
```

## Troubleshooting

### Common Issues

1. **"Cannot scan: Trivy vulnerability scanner not available"**
   - Make sure Trivy is installed and available in your PATH
   - Verify Trivy works by running `trivy --version`

2. **"Neither Docker nor Podman is available on this system"**
   - Make sure Docker or Podman is installed
   - Verify you have permission to use Docker/Podman (e.g., your user is in the docker group)

3. **"Error scanning image"**
   - Check if the image exists: `docker images` or `podman images`
   - Try running Trivy directly: `trivy image <image-name>`

### Getting Help

If you encounter any issues, please file a bug report at:
https://github.com/yourusername/container-inventory/issues
