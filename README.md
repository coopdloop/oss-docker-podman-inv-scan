# Container-Inventory

Container image inventory tool for Docker and Podman with enterprise packaging.

## Quick Start

**Development (macOS)**: See [README-DEV.md](README-DEV.md)  
**Production (Linux)**: See [README-PROD.md](README-PROD.md)

## Overview

- **Multi-Runtime**: Docker and Podman support
- **Auto-Detection**: Finds available container runtimes
- **Systemd Integration**: Automated scanning with timers
- **Cross-Platform Packages**: RPM and DEB packaging
- **Custom Scripts**: Plugin architecture for extensions

## Installation

### Development
```bash
make install
make test
make demo
```

### Production
```bash
# Install from package
sudo dnf install container-inventory-*.rpm
# or
sudo apt install ./container-inventory_*.deb
```

## Usage

```bash
# List all images
container-inventory

# Docker only
container-inventory --type docker

# Save to file
container-inventory --output inventory.json
```

## License

MIT License - see [LICENSE](LICENSE) file for details.