# Testing Container Inventory Systemd Service

This guide explains how to test and verify the container-inventory systemd service and timer setup.

## Testing the Service and Timer

### 1. After Package Installation

If you've installed the container-inventory through the RPM or DEB package, the timer should already be enabled and running. You can verify this with:

```bash
# Check if the timer is active
systemctl status container-inventory.timer

# See when the next execution is scheduled
systemctl list-timers container-inventory.timer
```

### 2. Running the Service Manually

To test the service without waiting for the timer:

```bash
# Run the service immediately
systemctl start container-inventory.service

# Check if it ran successfully
systemctl status container-inventory.service
```

### 3. Viewing the Output

Since we've configured all output to go to the journal, you can view the logs with:

```bash
# View all logs from the service
journalctl -u container-inventory.service

# View only the most recent execution
journalctl -u container-inventory.service -n 50

# Follow logs in real-time (useful for watching the next scheduled run)
journalctl -u container-inventory.service -f
```

### 4. Checking the Results

The service saves the inventory to `/var/lib/container-inventory/inventory.json`. You can examine this file to verify it's being updated:

```bash
# Check when the file was last modified
ls -la /var/lib/container-inventory/inventory.json

# View the content of the file
cat /var/lib/container-inventory/inventory.json | jq .
# (Install jq with 'apt install jq' or 'dnf install jq' if not available)
```

## Modifying the Service

### Changing the Execution Interval

If you want to change how often the service runs from the default 10 minutes:

```bash
# Edit the timer file
systemctl edit --full container-inventory.timer
```

Change the `OnUnitActiveSec=10min` line to your desired interval (e.g., `OnUnitActiveSec=1h` for hourly).

After editing, reload and restart the timer:

```bash
systemctl daemon-reload
systemctl restart container-inventory.timer
```

### Adjusting the Command Options

If you need to modify what the service does (e.g., changing output file location or adding options):

```bash
# Edit the service file
systemctl edit --full container-inventory.service
```

Modify the `ExecStart=` line with your desired command options.

After editing, reload the daemon:

```bash
systemctl daemon-reload
```

## Troubleshooting

### Service Failures

If the service is failing, check the detailed error logs:

```bash
journalctl -u container-inventory.service -n 50 --no-pager
```

Common issues:
- Missing permissions to access Docker/Podman
- Missing write permissions to the output directory

### Timer Not Running

If the timer doesn't seem to be running at the expected intervals:

```bash
# Check if the timer is enabled and active
systemctl status container-inventory.timer

# See all active timers and their next trigger times
systemctl list-timers
```

### Manual Testing of the Container Inventory Command

To verify the underlying command works correctly:

```bash
# Run the command manually as root
/usr/local/bin/container-inventory --scan --output /tmp/test-inventory.json

# Check the result
cat /tmp/test-inventory.json
```
