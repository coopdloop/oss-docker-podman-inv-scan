# Container-Inventory

![License](https://img.shields.io/github/license/yourusername/container-inventory)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

A comprehensive Docker and Podman container image inventory and vulnerability scanning tool with a rich CLI interface.

![Container Inventory Demo](docs/demo.png)

## Features

- **Multi-Runtime Support**: Works with both Docker and Podman
- **Automatic Detection**: Detects available container runtimes on your system
- **Vulnerability Scanning**: Scans images for security vulnerabilities using Trivy
- **Rich CLI Interface**: User-friendly, colorful command-line interface
- **Flexible Output**: Save inventory and scan results to JSON files
- **Append Mode**: Add new scan results to existing files
- **Selective Scanning**: Scan all images or just specific ones
- **Progress Indicators**: Visual feedback during operations

## Installation

### Prerequisites

- Python 3.6 or higher
- Docker and/or Podman
- [Trivy](https://github.com/aquasecurity/trivy) (optional, for vulnerability scanning)

### Using pip

```bash
pip install container-inventory
```

### From Source

```bash
git clone https://github.com/yourusername/container-inventory.git
cd container-inventory
pip install -e .
```

## Usage

### Basic Commands

List all container images:

```bash
container-inventory
```

List only Docker images:

```bash
container-inventory --type docker
```

List only Podman images:

```bash
container-inventory --type podman
```

### Vulnerability Scanning

Scan all images for vulnerabilities:

```bash
container-inventory --scan
```

Scan a specific image:

```bash
container-inventory --scan --image ubuntu:latest
```

### Output Options

Save inventory to a file:

```bash
container-inventory --output inventory.json
```

Save vulnerability scan results to a file:

```bash
container-inventory --scan --vulns-output vulnerabilities.json
```

Append to existing files:

```bash
container-inventory --output inventory.json --append
container-inventory --scan --vulns-output vulnerabilities.json --append
```

### Complete Usage

```
usage: container-inventory [-h] [--type {docker,podman,all}] [--output OUTPUT] [--append] [--scan] [--vulns-output VULNS_OUTPUT] [--image IMAGE]

Container Image Inventory and Vulnerability Scanner

optional arguments:
  -h, --help            show this help message and exit
  --type {docker,podman,all}, -t {docker,podman,all}
                        Type of container to inventory (default: all)
  --output OUTPUT, -o OUTPUT
                        Save inventory to specified file (default: None)
  --append, -a          Append to existing output file instead of overwriting (default: False)
  --scan, -s            Scan images for vulnerabilities (default: False)
  --vulns-output VULNS_OUTPUT, -v VULNS_OUTPUT
                        Save vulnerability scan results to specified file (default: None)
  --image IMAGE, -i IMAGE
                        Scan only the specified image (requires --scan) (default: None)
```

## Creating Test Images

The package includes a script to generate test Docker/Podman images with known vulnerabilities for testing:

```bash
container-inventory-create-test-images
```

Or run from the examples directory:

```bash
cd examples
./create_test_images.sh
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/container-inventory.git
cd container-inventory

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rich](https://github.com/Textualize/rich) for the beautiful terminal output
- [Trivy](https://github.com/aquasecurity/trivy) for vulnerability scanning capabilities
