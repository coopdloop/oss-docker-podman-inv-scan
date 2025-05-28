#!/usr/bin/env python3
"""
Example custom script for container inventory integration.

This demonstrates how to create a custom script that works with the
container inventory system. Replace this with your own script.

Usage:
    make YOUR_SCRIPT=path/to/your_script.py install-script
    make test-script
"""

from container_inventory.core import get_container_images
from container_inventory.cli import setup_logging
import json


def custom_analysis(images_data):
    """
    Example custom analysis function.
    Replace this with your own analysis logic.
    
    Args:
        images_data: List of container image data
        
    Returns:
        dict: Analysis results
    """
    results = {
        "total_images": len(images_data),
        "by_runtime": {},
        "size_analysis": {},
        "custom_metrics": []
    }
    
    # Count by runtime
    for image in images_data:
        runtime = image.get("runtime", "unknown")
        results["by_runtime"][runtime] = results["by_runtime"].get(runtime, 0) + 1
    
    # Size analysis
    total_size = sum(image.get("size", 0) for image in images_data)
    results["size_analysis"] = {
        "total_size_bytes": total_size,
        "average_size_bytes": total_size / len(images_data) if images_data else 0,
        "largest_image": max(images_data, key=lambda x: x.get("size", 0)) if images_data else None
    }
    
    # Custom metric example
    results["custom_metrics"] = [
        f"Found {len(images_data)} container images",
        f"Total storage usage: {total_size / (1024**3):.2f} GB",
        f"Average image size: {total_size / len(images_data) / (1024**2):.2f} MB" if images_data else "No images"
    ]
    
    return results


def main():
    """Main function for standalone execution"""
    setup_logging()
    
    print("Running custom container analysis...")
    
    # Get container images using the core functionality
    docker_images = get_container_images("docker")
    podman_images = get_container_images("podman")
    
    all_images = docker_images + podman_images
    
    # Run custom analysis
    results = custom_analysis(all_images)
    
    # Display results
    print("\nCustom Analysis Results:")
    print("=" * 50)
    print(json.dumps(results, indent=2, default=str))
    
    # Save results
    with open("custom_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: custom_analysis_results.json")


if __name__ == "__main__":
    main()