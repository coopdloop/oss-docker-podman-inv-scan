#!/usr/bin/env python3
"""
Command-line interface for Container Image Inventory.
"""

import argparse
import sys

from container_inventory.core import ContainerInventory, Colors


def setup_cli():
    """Set up the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Container Image Inventory",
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

    return parser.parse_args()


def main():
    """Main entry point for the script."""
    try:
        args = setup_cli()

        # Print header
        print(f"\n{Colors.BOLD}{Colors.BLUE}Container Image Inventory{Colors.RESET}\n")

        inventory = ContainerInventory(args.type)

        # Get all images or filter for a specific one
        all_images = inventory.get_images()

        if not all_images:
            print(f"{Colors.YELLOW}No container images found.{Colors.RESET}")
            return

        # Display inventory
        inventory.display_inventory(all_images)

        # Save inventory if requested
        if args.output:
            inventory.save_inventory(all_images, args.output, args.append)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.BOLD}{Colors.RED}Error:{Colors.RESET} {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
