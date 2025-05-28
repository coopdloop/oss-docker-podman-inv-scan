#!/usr/bin/env python3
"""
Core functionality for Container Image Inventory.
"""

import json
import os
import subprocess
import sys
import datetime
from typing import Dict, List


# Initialize colors for terminal output (if supported)
class Colors:
    """Simple ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @staticmethod
    def colored(text, color):
        """Apply color to text if terminal supports it."""
        if sys.stdout.isatty():
            return f"{color}{text}{Colors.RESET}"
        return text


class ContainerInventory:
    """Manage Docker and Podman container image inventory."""

    def __init__(self, container_type: str = "all"):
        """
        Initialize the container inventory manager.

        Args:
            container_type: Type of container to inventory ('docker', 'podman', or 'all')
        """
        self.container_type = container_type
        self.docker_available = self._check_tool_availability("docker")
        self.podman_available = self._check_tool_availability("podman")

        # Check if at least one container runtime is available
        if container_type != "all" and not getattr(self, f"{container_type}_available"):
            print(
                f"{Colors.BOLD}{Colors.RED}Error:{Colors.RESET} {container_type} is not available on this system"
            )
            # Only exit in non-test environments
            if "pytest" not in sys.modules:
                sys.exit(1)
        elif container_type == "all" and not (self.docker_available or self.podman_available):
            print(
                f"{Colors.BOLD}{Colors.RED}Error:{Colors.RESET} Neither Docker nor Podman is available on this system"
            )
            # Only exit in non-test environments
            if "pytest" not in sys.modules:
                sys.exit(1)

    def _check_tool_availability(self, tool: str) -> bool:
        """Check if a command-line tool is available."""
        try:
            subprocess.run(
                [tool, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )
            return True
        except FileNotFoundError:
            return False

    def get_images(self) -> List[Dict]:
        """Get a list of all container images."""
        images = []

        if self.container_type in ["docker", "all"] and self.docker_available:
            docker_images = self._get_docker_images()
            for image in docker_images:
                image["source"] = "docker"
                images.append(image)

        if self.container_type in ["podman", "all"] and self.podman_available:
            podman_images = self._get_podman_images()
            for image in podman_images:
                image["source"] = "podman"
                images.append(image)

        return images

    def _get_docker_images(self) -> List[Dict]:
        """Get a list of Docker images."""
        print(f"{Colors.BLUE}Fetching Docker images...{Colors.RESET}")

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{json .}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            images = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    image_data = json.loads(line)
                    images.append(image_data)

            return images
        except subprocess.CalledProcessError as e:
            print(
                f"{Colors.BOLD}{Colors.RED}Error fetching Docker images:{Colors.RESET} {e.stderr}"
            )
            return []

    def _get_podman_images(self) -> List[Dict]:
        """Get a list of Podman images."""
        print(f"{Colors.BLUE}Fetching Podman images...{Colors.RESET}")

        try:
            result = subprocess.run(
                ["podman", "images", "--format", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            images = json.loads(result.stdout)

            # Normalize podman data to match docker format
            normalized_images = []
            for img in images:
                normalized = {
                    "Repository": (
                        img.get("Names", ["<none>"])[0].split(":")[0]
                        if img.get("Names")
                        else "<none>"
                    ),
                    "Tag": (
                        img.get("Names", [":<none>"])[0].split(":")[-1]
                        if img.get("Names")
                        else "<none>"
                    ),
                    "ID": str(img.get("Id", ""))[:12],
                    "CreatedAt": str(img.get("Created", "")),
                    "Size": self._format_size(int(img.get("Size", 0))),
                    "source": "podman",
                }
                normalized_images.append(normalized)

            return normalized_images
        except subprocess.CalledProcessError as e:
            print(
                f"{Colors.BOLD}{Colors.RED}Error fetching Podman images:{Colors.RESET} {e.stderr}"
            )
            return []
        except json.JSONDecodeError:
            print(f"{Colors.BOLD}{Colors.RED}Error:{Colors.RESET} Could not parse Podman output")
            return []

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        size = float(size_bytes)  # Create a separate float variable
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}PB"

    def display_inventory(self, images: List[Dict]) -> None:
        """Display the container image inventory in a formatted table."""
        if not images:
            print("No images found.")
            return

        # Get max width for each column for proper formatting
        col_widths = {
            "ID": max(12, max(len(str(img.get("ID", ""))) for img in images)),
            "Repository": max(10, max(len(str(img.get("Repository", ""))) for img in images)),
            "Tag": max(3, max(len(str(img.get("Tag", ""))) for img in images)),
            "Created At": max(10, max(len(str(img.get("CreatedAt", ""))) for img in images)),
            "Size": max(4, max(len(str(img.get("Size", ""))) for img in images)),
            "Source": max(6, max(len(str(img.get("source", ""))) for img in images)),
        }

        # Print header
        print("\n" + Colors.BOLD + "Container Image Inventory" + Colors.RESET + "\n")

        # Print column headers
        header = (
            f"{Colors.CYAN}{'ID':<{col_widths['ID']}}{Colors.RESET} | "
            f"{Colors.GREEN}{'Repository':<{col_widths['Repository']}}{Colors.RESET} | "
            f"{Colors.BLUE}{'Tag':<{col_widths['Tag']}}{Colors.RESET} | "
            f"{Colors.MAGENTA}{'Created At':<{col_widths['Created At']}}{Colors.RESET} | "
            f"{Colors.YELLOW}{'Size':<{col_widths['Size']}}{Colors.RESET} | "
            f"{Colors.RED}{'Source':<{col_widths['Source']}}{Colors.RESET}"
        )
        print(header)

        # Print separator
        separator = "-" * (sum(col_widths.values()) + len(col_widths) * 3)
        print(separator)

        # Print rows
        for image in images:
            row = (
                f"{str(image.get('ID', '')):<{col_widths['ID']}} | "
                f"{str(image.get('Repository', '')):<{col_widths['Repository']}} | "
                f"{str(image.get('Tag', '')):<{col_widths['Tag']}} | "
                f"{str(image.get('CreatedAt', '')):<{col_widths['Created At']}} | "
                f"{str(image.get('Size', '')):<{col_widths['Size']}} | "
                f"{str(image.get('source', '')):<{col_widths['Source']}}"
            )
            print(row)

        print("")  # Add empty line after table

    def save_inventory(self, images: List[Dict], output_file: str, append: bool = False) -> None:
        """
        Save inventory to a file.

        Args:
            images: List of image data dictionaries
            output_file: Path to output file
            append: Whether to append to existing file
        """
        mode = "a" if append and os.path.exists(output_file) else "w"

        try:
            with open(output_file, mode) as f:
                # If appending and file exists but is empty, write the opening bracket
                if append and os.path.exists(output_file) and os.path.getsize(output_file) == 0:
                    mode = "w"

                # If appending to a non-empty JSON file, we need to handle the JSON structure
                if append and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    # Read existing content
                    f.seek(0)
                    try:
                        existing_data = json.load(f)

                        # If it's a list, append to it
                        if isinstance(existing_data, list):
                            combined_data = existing_data + images
                            f.seek(0)
                            f.truncate(0)
                            json.dump(combined_data, f, indent=2)
                            print(
                                f"{Colors.GREEN}Successfully appended to {output_file}{Colors.RESET}"
                            )
                            return
                        else:
                            print(
                                f"{Colors.YELLOW}Warning: Existing file is not a JSON array. Creating new file.{Colors.RESET}"
                            )
                            mode = "w"
                    except json.JSONDecodeError:
                        print(
                            f"{Colors.YELLOW}Warning: Existing file is not valid JSON. Creating new file.{Colors.RESET}"
                        )
                        mode = "w"

                # Write new content
                if mode == "w":
                    with open(output_file, "w") as f:
                        json.dump(images, f, indent=2)
                        print(f"{Colors.GREEN}Successfully saved to {output_file}{Colors.RESET}")

        except IOError as e:
            print(f"{Colors.BOLD}{Colors.RED}Error saving inventory:{Colors.RESET} {e}")
