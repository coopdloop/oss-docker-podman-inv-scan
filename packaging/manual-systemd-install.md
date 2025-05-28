# Manual Installation of Container Inventory Systemd Units

If you've installed the container-inventory tool manually (not via RPM or DEB package),
you can set up the systemd service and timer using these instructions.

## 1. Install Service and Timer Files

```bash
# Copy the service file
sudo cp container-inventory.service /etc/systemd/system/
sudo cp container-inventory.timer /etc/systemd/system/

# Create data directory
sudo mkdir -p /var/lib/container-inventory

# Set proper permissions
sudo chmod 644 /etc/systemd/system/container-inventory.service
sudo chmod 644 /etc/systemd/system/container-inventory.timer

# Reload systemd to recognize new files
sudo systemctl daemon-reload
```

## 2. Enable and Start the Timer

```bash
# Enable the timer to start at boot
sudo systemctl enable container-inventory.timer

# Start the timer immediately
sudo systemctl start container-inventory.timer
```

## 3. Verify Installation

```bash
# Check timer status
sudo systemctl status container-inventory.timer

# See when the next run is scheduled
sudo systemctl list-timers | grep container-inventory
```

## 4. Run the Service Once to Test

```bash
# Run the service once manually to verify it works
sudo systemctl start container-inventory.service

# Check the service status
sudo systemctl status container-inventory.service
```

## 5. Check the Logs

```bash
# View the logs for the service
sudo journalctl -u container-inventory.service

# Follow the logs in real-time
sudo journalctl -u container-inventory.service -f
```
