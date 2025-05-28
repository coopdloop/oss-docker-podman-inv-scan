#!/bin/bash
# Script to run the container-inventory test container with systemd

set -e

CONTAINER_NAME="container-inventory-test"
IMAGE_NAME="container-inventory-test"

# Function to cleanup existing container
cleanup() {
    echo "Cleaning up existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
}

# Function to run the container
run_container() {
    local interactive_mode=$1

    echo "Starting Container Inventory Test Environment..."
    echo "==============================================="

    # Cleanup any existing container
    cleanup

    # Always start with systemd first, then provide interactive access if requested
    echo "Starting container with systemd..."

    # Run the container with systemd
    docker run -d \
        --name "$CONTAINER_NAME" \
        --privileged \
        --cgroupns=host \
        -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$(pwd)/test-data:/var/lib/container-inventory" \
        --tmpfs /tmp \
        --tmpfs /run \
        --tmpfs /run/lock \
        "$IMAGE_NAME"

    echo ""
    echo "Container started successfully!"
    echo ""

    # Wait for systemd to initialize
    echo "Waiting for systemd to initialize..."
    sleep 5

    # Check if systemd started successfully
    echo "Checking systemd status..."
    if docker exec "$CONTAINER_NAME" systemctl is-system-running --wait >/dev/null 2>&1; then
        echo "✓ Systemd is running"
    else
        echo "⚠ Systemd may not be fully initialized yet, checking status..."
        docker exec "$CONTAINER_NAME" systemctl status --no-pager || true
    fi

    # Check timer status
    echo ""
    echo "Checking timer status..."
    docker exec "$CONTAINER_NAME" systemctl status container-inventory.timer --no-pager || true

    if [ "$interactive_mode" = "true" ]; then
        echo ""
        echo "=== INTERACTIVE MODE ==="
        echo "Systemd is running in the background."
        echo "You can now run systemctl commands."
        echo "Type 'exit' to leave the container."
        echo "========================"
        echo ""
        # Provide interactive shell
        docker exec -it "$CONTAINER_NAME" bash
    else
        echo ""
        echo "=== DAEMON MODE ==="
        echo "Container is running in the background with systemd active."
        echo ""
        echo "Useful commands:"
        echo "  docker exec -it $CONTAINER_NAME bash                    - Enter the container"
        echo "  docker exec -it $CONTAINER_NAME container-inventory-help - Show help"
        echo "  docker logs $CONTAINER_NAME                            - View container logs"
        echo "  docker stop $CONTAINER_NAME                            - Stop the container"
        echo ""
        echo "To check systemd timer:"
        echo "  docker exec -it $CONTAINER_NAME systemctl status container-inventory.timer"
        echo ""
        echo "To monitor the service:"
        echo "  ./monitor-container-inventory.sh"
        echo "================="
    fi
}

# Parse command line arguments
INTERACTIVE=false
case "${1:-}" in
    --interactive|-i)
        INTERACTIVE=true
        ;;
    --help|-h)
        echo "Usage: $0 [--interactive|-i] [--help|-h]"
        echo ""
        echo "Options:"
        echo "  --interactive, -i    Run container in interactive mode"
        echo "  --help, -h          Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                   Run container in daemon mode"
        echo "  $0 --interactive     Run container interactively"
        exit 0
        ;;
    "")
        # Default case - daemon mode
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

# Check if image exists
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "Error: Image '$IMAGE_NAME' not found."
    echo "Please run './build-test-image.sh' first."
    exit 1
fi

# Create test data directory
mkdir -p test-data

# Run the container
run_container "$INTERACTIVE"
