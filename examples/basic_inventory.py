#!/usr/bin/env python3
"""
Basic example showing how to use the Container Inventory API.
"""

from container_inventory.core import ContainerInventory


def main():
    """Basic inventory example."""
    print("Creating Container Inventory...")
    inventory = ContainerInventory(container_type="all")

    print("\nGetting container images...")
    images = inventory.get_images()

    print(f"\nFound {len(images)} container images")

    # Display inventory
    print("\nDisplaying inventory...")
    inventory.display_inventory(images)

    # Filter for specific images (example: Alpine-based images)
    alpine_images = [img for img in images if "alpine" in img.get("Repository", "").lower()]

    if alpine_images:
        print("\nAlpine-based images:")
        inventory.display_inventory(alpine_images)

    # Save inventory to file
    print("\nSaving inventory to file...")
    inventory.save_inventory(images, "inventory_example.json")

    print("\nInventory saved to inventory_example.json")


if __name__ == "__main__":
    main()
