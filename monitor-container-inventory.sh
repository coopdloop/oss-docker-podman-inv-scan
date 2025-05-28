#!/bin/bash
# Monitor the container inventory service and timer in the test container

set -e

CONTAINER_NAME="container-inventory-test"

# Check if container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
    echo "Error: Container '$CONTAINER_NAME' is not running."
    echo "Please run './run-test-container.sh' first."
    exit 1
fi

echo "Container Inventory Service Monitor"
echo "=================================="
echo "Container: $CONTAINER_NAME"
echo "Press Ctrl+C to exit"
echo ""

# Function to show status
show_status() {
    echo "=== $(date) ==="
    echo ""
    
    echo "Timer Status:"
    docker exec "$CONTAINER_NAME" systemctl status container-inventory.timer --no-pager --lines=3
    echo ""
    
    echo "Service Status:"
    docker exec "$CONTAINER_NAME" systemctl status container-inventory.service --no-pager --lines=3
    echo ""
    
    echo "Recent Journal Logs (last 10 entries):"
    docker exec "$CONTAINER_NAME" journalctl -u container-inventory.service --no-pager -n 10 --since "5 minutes ago"
    echo ""
    
    echo "Data Directory Contents:"
    docker exec "$CONTAINER_NAME" ls -la /var/lib/container-inventory/ 2>/dev/null || echo "No data files found"
    echo ""
    
    echo "Next timer run:"
    docker exec "$CONTAINER_NAME" systemctl list-timers container-inventory.timer --no-pager
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Initial status
show_status

# Monitor loop
while true; do
    sleep 30
    show_status
done