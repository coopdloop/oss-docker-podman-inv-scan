#!/usr/bin/env python3
"""
Core functionality for Container Image Inventory and Vulnerability Scanner.
"""

import json
import os
import subprocess
import sys
import datetime
from typing import Dict, List

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Initialize Rich console
console = Console()


class ContainerInventory:
    """Manage Docker and Podman container image inventory and vulnerability scanning."""

    def __init__(self, container_type: str = "all"):
        """
        Initialize the container inventory manager.

        Args:
            container_type: Type of container to inventory ('docker', 'podman', or 'all')
        """
        self.container_type = container_type
        self.docker_available = self._check_tool_availability("docker")
        self.podman_available = self._check_tool_availability("podman")
        self.trivy_available = self._check_tool_availability("trivy")

        # Check if at least one container runtime is available
        if container_type != "all" and not getattr(self, f"{container_type}_available"):
            console.print(f"[bold red]Error:[/] {container_type} is not available on this system")
            sys.exit(1)
        elif container_type == "all" and not (self.docker_available or self.podman_available):
            console.print(
                "[bold red]Error:[/] Neither Docker nor Podman is available on this system"
            )
            sys.exit(1)

        # Check if vulnerability scanner is available
        if not self.trivy_available:
            console.print(
                "[bold yellow]Warning:[/] Trivy vulnerability scanner not found. "
                "Vulnerability scanning will be disabled."
            )

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
        with Progress(
            SpinnerColumn(), TextColumn("[bold blue]Fetching Docker images...[/]"), transient=True
        ) as progress:
            progress.add_task("", total=None)

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
                console.print(f"[bold red]Error fetching Docker images:[/] {e.stderr}")
                return []

    def _get_podman_images(self) -> List[Dict]:
        """Get a list of Podman images."""
        with Progress(
            SpinnerColumn(), TextColumn("[bold blue]Fetching Podman images...[/]"), transient=True
        ) as progress:
            progress.add_task("", total=None)

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
                console.print(f"[bold red]Error fetching Podman images:[/] {e.stderr}")
                return []
            except json.JSONDecodeError:
                console.print("[bold red]Error:[/] Could not parse Podman output")
                return []

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        size = float(size_bytes)  # Create a separate float variable
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}PB"

    def scan_image_vulnerabilities(self, image_id: str, image_source: str | None) -> Dict:
        """
        Scan a container image for vulnerabilities using Trivy.

        Args:
            image_id: The ID or name of the image to scan
            image_source: The source of the image ("docker" or "podman")

        Returns:
            Dictionary with vulnerability information
        """
        if not self.trivy_available:
            return {"error": "Trivy scanner not available", "vulnerabilities": []}

        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold yellow]Scanning {image_id} for vulnerabilities...[/]"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Scanning", total=100)

            try:
                # Use different approaches for Docker vs Podman
                if image_source == "podman":
                    # For Podman, export the image to a tarball and scan that instead
                    console.print("[blue]Using Podman export method for scanning...[/]")

                    # Create a temporary directory for the image tarball
                    import tempfile
                    import os

                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Export the Podman image to a tarball
                        image_tar = os.path.join(temp_dir, "image.tar")
                        export_cmd = ["podman", "save", "-o", image_tar, image_id]

                        export_result = subprocess.run(
                            export_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=False,
                        )

                        if export_result.returncode != 0:
                            return {
                                "error": f"Error exporting Podman image: {export_result.stderr}",
                                "vulnerabilities": [],
                            }

                        # Now scan the tarball with Trivy
                        result = subprocess.run(
                            ["trivy", "image", "--input", image_tar, "--format", "json"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=False,
                        )
                else:
                    # Default approach for Docker
                    result = subprocess.run(
                        ["trivy", "image", "--format", "json", image_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,  # Don't raise exception on non-zero return code (Trivy returns non-zero when vulns found)
                    )

                progress.update(task, completed=100)

                if result.returncode != 0 and not result.stdout:
                    return {
                        "error": f"Error scanning image: {result.stderr}",
                        "vulnerabilities": [],
                    }

                try:
                    scan_result = json.loads(result.stdout)
                    return {
                        "image": image_id,
                        "scan_time": datetime.datetime.now().isoformat(),
                        "results": scan_result,
                    }
                except json.JSONDecodeError:
                    return {"error": "Could not parse scanner output", "vulnerabilities": []}

            except Exception as e:
                return {"error": f"Error during scan: {str(e)}", "vulnerabilities": []}

    def display_inventory(self, images: List[Dict]) -> None:
        """Display the container image inventory in a rich table."""
        table = Table(title="Container Image Inventory")

        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Repository", style="green")
        table.add_column("Tag", style="blue")
        table.add_column("Created At", style="magenta")
        table.add_column("Size", style="yellow")
        table.add_column("Source", style="red")

        for image in images:
            table.add_row(
                str(image.get("ID", "")),
                str(image.get("Repository", "")),
                str(image.get("Tag", "")),
                str(image.get("CreatedAt", "")),
                str(image.get("Size", "")),
                str(image.get("source", "")),
            )

        console.print(table)

    def display_vulnerabilities(self, scan_result: Dict) -> None:
        """Display vulnerability scan results."""
        if "error" in scan_result and scan_result["error"]:
            console.print(f"[bold red]Error:[/] {scan_result['error']}")
            return

        console.print(f"\n[bold]Vulnerability Scan Results for {scan_result['image']}[/]")
        console.print(f"Scan completed at: {scan_result['scan_time']}\n")

        if "results" not in scan_result or not scan_result["results"]:
            console.print("[green]No vulnerabilities found.[/]")
            return

        # Process Trivy results
        for result in scan_result["results"]:
            if "Target" in result:
                console.print(f"[bold]Target:[/] {result['Target']}")

            if "Vulnerabilities" not in result or not result["Vulnerabilities"]:
                console.print("[green]No vulnerabilities found in this target.[/]")
                continue

            vuln_table = Table(title=f"Vulnerabilities in {result.get('Target', 'Unknown')}")
            vuln_table.add_column("ID", style="cyan", no_wrap=True)
            vuln_table.add_column("Package", style="blue")
            vuln_table.add_column("Installed", style="blue")
            vuln_table.add_column("Fixed In", style="green")
            vuln_table.add_column("Severity", style="yellow")
            vuln_table.add_column("Title", style="white")

            # Sort vulnerabilities by severity
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
            sorted_vulns = sorted(
                result["Vulnerabilities"],
                key=lambda v: severity_order.get(v.get("Severity", "UNKNOWN").upper(), 999),
            )

            for vuln in sorted_vulns:
                severity = vuln.get("Severity", "UNKNOWN").upper()
                severity_style = {
                    "CRITICAL": "bold red",
                    "HIGH": "red",
                    "MEDIUM": "yellow",
                    "LOW": "green",
                    "UNKNOWN": "blue",
                }.get(severity, "blue")

                vuln_table.add_row(
                    vuln.get("VulnerabilityID", ""),
                    vuln.get("PkgName", ""),
                    vuln.get("InstalledVersion", ""),
                    vuln.get("FixedVersion", ""),
                    f"[{severity_style}]{severity}[/{severity_style}]",
                    vuln.get("Title", "")[:50] + ("..." if len(vuln.get("Title", "")) > 50 else ""),
                )

            console.print(vuln_table)
            console.print("")  # Add space between tables

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
                            console.print(f"[green]Successfully appended to {output_file}[/]")
                            return
                        else:
                            console.print(
                                "[yellow]Warning: Existing file is not a JSON array. Creating new file.[/]"
                            )
                            mode = "w"
                    except json.JSONDecodeError:
                        console.print(
                            "[yellow]Warning: Existing file is not valid JSON. Creating new file.[/]"
                        )
                        mode = "w"

                # Write new content
                if mode == "w":
                    with open(output_file, "w") as f:
                        json.dump(images, f, indent=2)
                        console.print(f"[green]Successfully saved to {output_file}[/]")

        except IOError as e:
            console.print(f"[bold red]Error saving inventory:[/] {e}")

    def save_vulnerabilities(
        self, scan_results: List[Dict], output_file: str, append: bool = False
    ) -> None:
        """
        Save vulnerability scan results to a file.

        Args:
            scan_results: List of vulnerability scan result dictionaries
            output_file: Path to output file
            append: Whether to append to existing file
        """
        mode = "a" if append and os.path.exists(output_file) else "w"

        try:
            # Similar logic to save_inventory
            with open(output_file, mode) as f:
                if append and os.path.exists(output_file) and os.path.getsize(output_file) == 0:
                    mode = "w"

                if append and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    f.seek(0)
                    try:
                        existing_data = json.load(f)

                        if isinstance(existing_data, list):
                            combined_data = existing_data + scan_results
                            f.seek(0)
                            f.truncate(0)
                            json.dump(combined_data, f, indent=2)
                            console.print(f"[green]Successfully appended to {output_file}[/]")
                            return
                        else:
                            console.print(
                                "[yellow]Warning: Existing file is not a JSON array. Creating new file.[/]"
                            )
                            mode = "w"
                    except json.JSONDecodeError:
                        console.print(
                            "[yellow]Warning: Existing file is not valid JSON. Creating new file.[/]"
                        )
                        mode = "w"

                if mode == "w":
                    with open(output_file, "w") as f:
                        json.dump(scan_results, f, indent=2)
                        console.print(f"[green]Successfully saved to {output_file}[/]")

        except IOError as e:
            console.print(f"[bold red]Error saving vulnerability results:[/] {e}")
