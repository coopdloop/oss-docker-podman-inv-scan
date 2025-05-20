#!/usr/bin/env python3
"""
Command-line interface for Container Image Inventory and Vulnerability Scanner.
"""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from container_inventory.core import ContainerInventory

# Initialize Rich console
console = Console()


def setup_cli():
    """Set up the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Container Image Inventory and Vulnerability Scanner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=["docker", "podman", "all"],
        default="all",
        help="Type of container to inventory",
    )

    parser.add_argument("--output", "-o", help="Save inventory to specified file")

    parser.add_argument(
        "--append",
        "-a",
        action="store_true",
        help="Append to existing output file instead of overwriting",
    )

    parser.add_argument(
        "--scan", "-s", action="store_true", help="Scan images for vulnerabilities"
    )

    parser.add_argument(
        "--vulns-output", "-v", help="Save vulnerability scan results to specified file"
    )

    parser.add_argument(
        "--image", "-i", help="Scan only the specified image (requires --scan)"
    )

    return parser.parse_args()


def main():
    """Main entry point for the script."""
    try:
        args = setup_cli()

        # Print header
        console.print(
            Panel.fit(
                "[bold blue]Container Image Inventory and Vulnerability Scanner[/]",
                border_style="blue",
            )
        )

        inventory = ContainerInventory(args.type)

        # Get all images or filter for a specific one
        all_images = inventory.get_images()

        if not all_images:
            console.print("[yellow]No container images found.[/]")
            return

        # Display inventory
        inventory.display_inventory(all_images)

        # Save inventory if requested
        if args.output:
            inventory.save_inventory(all_images, args.output, args.append)

        # Scan for vulnerabilities if requested
        if args.scan:
            if not inventory.trivy_available:
                console.print(
                    "[bold red]Cannot scan: Trivy vulnerability scanner not available[/]"
                )
                return

            scan_results = []

            if args.image:
                # Scan only the specified image
                image_exists = any(
                    i.get("ID", "") == args.image
                    or f"{i.get('Repository', '')}:{i.get('Tag', '')}" == args.image
                    for i in all_images
                )

                if not image_exists:
                    console.print(
                        f"[bold red]Error:[/] Image '{args.image}' not found in inventory"
                    )
                    return

                console.print(f"\nScanning image: {args.image}")
                scan_result = inventory.scan_image_vulnerabilities(args.image)
                inventory.display_vulnerabilities(scan_result)
                scan_results.append(scan_result)
            else:
                # Scan all images
                for image in all_images:
                    image_id = image.get("ID", "")
                    if not image_id:
                        continue

                    # For podman, we may need to use the full ID
                    if image.get("source") == "podman":
                        image_id = image.get("ID", "")

                    scan_result = inventory.scan_image_vulnerabilities(image_id)
                    inventory.display_vulnerabilities(scan_result)
                    scan_results.append(scan_result)

            # Save vulnerability results if requested
            if args.vulns_output:
                inventory.save_vulnerabilities(
                    scan_results, args.vulns_output, args.append
                )

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
