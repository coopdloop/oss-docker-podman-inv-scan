#!/usr/bin/env python3
"""
Script to create test Docker and Podman images for use with Container Inventory tool.
"""

import subprocess
import tempfile
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

# Initialize Rich console
console = Console()


def check_tool_availability(tool: str) -> bool:
    """Check if a command-line tool is available."""
    try:
        subprocess.run(
            [tool, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def create_dockerfile(temp_dir: Path, name: str, content: str) -> Path:
    """Create a Dockerfile with given content."""
    dockerfile_path = temp_dir / f"Dockerfile.{name}"
    with open(dockerfile_path, "w") as f:
        f.write(content)
    return dockerfile_path


def create_test_images():
    """Create test Docker and Podman images."""
    # Check for Docker and Podman
    docker_available = check_tool_availability("docker")
    podman_available = check_tool_availability("podman")

    if not docker_available and not podman_available:
        console.print("[bold red]Error:[/] Neither Docker nor Podman is available on this system")
        sys.exit(1)

    # Create a temporary directory for files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        console.print("[bold]Creating test files...[/]")

        # Create server.js
        server_js = """
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
"""
        with open(temp_path / "server.js", "w") as f:
            f.write(server_js)

        # Create Dockerfiles
        dockerfiles = {
            "alpine": """
FROM alpine:3.14
RUN apk add --no-cache python3 curl
WORKDIR /app
COPY . /app
CMD ["sh", "-c", "echo 'Alpine test container running'; sleep infinity"]
""",
            "ubuntu": """
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \\
    python3 \\
    curl \\
    openssl \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
CMD ["bash", "-c", "echo 'Ubuntu test container running'; sleep infinity"]
""",
            "node": """
FROM node:14.17.0
WORKDIR /app
COPY package.json ./
RUN echo '{\\
  "name": "vulnerable-app",\\
  "version": "1.0.0",\\
  "dependencies": {\\
    "express": "4.14.0",\\
    "lodash": "4.17.0",\\
    "minimist": "0.2.1"\\
  }\\
}' > package.json
RUN npm install
COPY . .
CMD ["node", "server.js"]
""",
            "multistage": """
FROM golang:1.16 AS builder
WORKDIR /app
COPY . .
RUN go mod init example.com/hello && \\
    echo 'package main\\n\\nimport "fmt"\\n\\nfunc main() {\\n\\tfmt.Println("Hello, World!")\\n}' > main.go && \\
    CGO_ENABLED=0 go build -o hello .

FROM debian:10.7
COPY --from=builder /app/hello /usr/local/bin/
RUN apt-get update && apt-get install -y \\
    curl \\
    libssl1.1 \\
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/local/bin/hello"]
""",
        }

        # Create all Dockerfiles
        for name, content in dockerfiles.items():
            create_dockerfile(temp_path, name, content)

        # Build images
        with Progress() as progress:
            if docker_available:
                console.print("\n[bold]Building Docker images...[/]")
                docker_task = progress.add_task(
                    "[cyan]Building Docker images...", total=len(dockerfiles)
                )

                for name in dockerfiles.keys():
                    console.print(f"[blue]Building Docker image:[/] test-{name}")
                    subprocess.run(
                        [
                            "docker",
                            "build",
                            "-t",
                            f"test-{name}:latest",
                            "-f",
                            f"Dockerfile.{name}",
                            ".",
                        ],
                        cwd=temp_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                    )
                    progress.update(docker_task, advance=1)

            if podman_available:
                console.print("\n[bold]Building Podman images...[/]")
                podman_task = progress.add_task(
                    "[magenta]Building Podman images...", total=len(dockerfiles)
                )

                for name in dockerfiles.keys():
                    console.print(f"[blue]Building Podman image:[/] test-{name}")
                    subprocess.run(
                        [
                            "podman",
                            "build",
                            "-t",
                            f"test-{name}:latest",
                            "-f",
                            f"Dockerfile.{name}",
                            ".",
                        ],
                        cwd=temp_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                    )
                    progress.update(podman_task, advance=1)

        console.print("\n[bold green]Successfully created test images![/]")
        console.print(
            "\nYou can now run the container inventory tool to view and scan these images:"
        )
        console.print("[blue]container_inventory --scan[/]")


def main():
    """Main entry point for the script."""
    try:
        console.print(Panel.fit("[bold blue]Container Image Test Builder[/]", border_style="blue"))

        create_test_images()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error building images:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
