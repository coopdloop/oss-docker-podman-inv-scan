#!/usr/bin/env python3
"""
Example showing how to scan container images for vulnerabilities.
"""

from container_inventory.core import ContainerInventory


def main():
    """Vulnerability scanning example."""
    print("Creating Container Inventory...")
    inventory = ContainerInventory(container_type="all")

    # Check if vulnerability scanning is available
    if not inventory.trivy_available:
        print(
            "Trivy vulnerability scanner not available. Please install Trivy to run this example."
        )
        return

    print("\nGetting container images...")
    images = inventory.get_images()

    if not images:
        print("No container images found.")
        return

    print(f"\nFound {len(images)} container images")

    # Display inventory
    print("\nDisplaying inventory...")
    inventory.display_inventory(images)

    # Ask user which image to scan
    print("\nSelect an image to scan by entering its ID:")
    image_id = input("> ")

    # Find the image in our inventory
    image = next((img for img in images if img.get("ID", "") == image_id), None)

    if not image:
        print(f"Image with ID '{image_id}' not found.")
        return

    print(f"\nScanning image: {image.get('Repository', '')}:{image.get('Tag', '')} ({image_id})")

    # Scan the image
    scan_result = inventory.scan_image_vulnerabilities(image_id)

    # Display results
    inventory.display_vulnerabilities(scan_result)

    # Save results
    print("\nSaving vulnerability scan results...")
    inventory.save_vulnerabilities([scan_result], "vulnerabilities_example.json")

    print("\nScan results saved to vulnerabilities_example.json")


if __name__ == "__main__":
    main()
