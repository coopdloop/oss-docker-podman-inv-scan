# Container-Inventory - Development

Development and testing environment for macOS with Docker-based package building.

## Quick Start

```bash
# Complete demo pipeline
make demo

# Custom script integration
make YOUR_SCRIPT=path/to/script.py install-script
make test-script
```

## Development Setup

```bash
# Setup environment
make install
make test

# Test Docker packaging locally
make docker-test
./monitor-container-inventory.sh
```

## Key Development Commands

| Command | Purpose |
|---------|---------|
| `make demo` | Full demonstration pipeline |
| `make docker-build` | Build test container with systemd |
| `make docker-test` | Test RPM/DEB packages in Docker |
| `make package` | Build distribution packages |
| `make clean` | Clean build artifacts |

## Custom Script Integration

1. Place scripts in `container_inventory/custom/`
2. Install: `make YOUR_SCRIPT=script.py install-script`
3. Test: `make test-script`

See `container_inventory/custom/example_script.py` for integration example.

## Testing

- **Unit tests**: `make test`
- **Docker integration**: `make docker-test`
- **Package building**: `make package`
- **Service monitoring**: `./monitor-container-inventory.sh`

## Build Outputs

Packages created in `packaging/packages/`:
- `container-inventory-*.rpm` (RHEL/Fedora/CentOS)
- `container-inventory_*.deb` (Debian/Ubuntu)