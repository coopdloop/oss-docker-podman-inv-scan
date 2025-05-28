# Container-Inventory - Production Installation

Container image inventory tool for Docker and Podman with systemd integration.

## Installation

### RPM (RHEL/Fedora/CentOS)

```bash
# Install package
sudo dnf install container-inventory-*.rpm

# Verify installation
container-inventory --help
```

### DEB (Debian/Ubuntu)

```bash
# Install package
sudo apt install ./container-inventory_*.deb

# Verify installation
container-inventory --help
```

## Usage

```bash
# List all images
container-inventory

# Docker only
container-inventory --type docker

# Podman only  
container-inventory --type podman

# Save to file
container-inventory --output inventory.json
```

## Systemd Service

The package installs a systemd timer that runs every 6 hours:

```bash
# Check service status
systemctl status container-inventory.service
systemctl status container-inventory.timer

# View logs
journalctl -u container-inventory.service -f

# Manual run
sudo systemctl start container-inventory.service
```

## Configuration

Service outputs to `/var/lib/container-inventory/inventory.json`

## Requirements

- Python 3.6+
- Docker and/or Podman
- Systemd (for automated scanning)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Neither Docker nor Podman available" | Install Docker or Podman |
| Permission denied | Add user to docker group: `sudo usermod -aG docker $USER` |
| Service not running | Check: `systemctl status container-inventory.timer` |