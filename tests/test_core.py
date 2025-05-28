"""
Tests for the core module of Container Inventory.
"""

import unittest
from unittest.mock import patch, MagicMock

from container_inventory.core import ContainerInventory


class TestContainerInventory(unittest.TestCase):
    """Tests for the ContainerInventory class."""

    @patch("container_inventory.core.subprocess.run")
    def test_check_tool_availability(self, mock_run):
        """Test checking if a tool is available."""
        # Tool is available
        mock_run.return_value = MagicMock()
        inventory = ContainerInventory()
        self.assertTrue(inventory._check_tool_availability("docker"))

        # Tool is not available
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(inventory._check_tool_availability("nonexistent-tool"))

    @patch("container_inventory.core.subprocess.run")
    def test_init(self, mock_run):
        """Test initialization of ContainerInventory."""
        with patch(
            "container_inventory.core.ContainerInventory._check_tool_availability"
        ) as mock_check:
            # Both Docker and Podman available
            mock_check.side_effect = lambda tool: tool in ["docker", "podman"]
            inventory = ContainerInventory()
            self.assertEqual(inventory.container_type, "all")
            self.assertTrue(inventory.docker_available)
            self.assertTrue(inventory.podman_available)

            # Only Docker available
            mock_check.side_effect = lambda tool: tool == "docker"
            inventory = ContainerInventory()
            self.assertTrue(inventory.docker_available)
            self.assertFalse(inventory.podman_available)

            # Only Podman available
            mock_check.side_effect = lambda tool: tool == "podman"
            inventory = ContainerInventory()
            self.assertFalse(inventory.docker_available)
            self.assertTrue(inventory.podman_available)

    @patch("container_inventory.core.ContainerInventory._check_tool_availability")
    @patch("container_inventory.core.ContainerInventory._get_docker_images")
    @patch("container_inventory.core.ContainerInventory._get_podman_images")
    def test_get_images(self, mock_podman, mock_docker, mock_check):
        """Test getting container images."""
        # Set up mocks
        mock_check.return_value = True

        # Create dummy data
        docker_images = [{"ID": "123", "Repository": "docker-image", "Tag": "latest"}]
        podman_images = [{"ID": "456", "Repository": "podman-image", "Tag": "latest"}]

        mock_docker.return_value = docker_images
        mock_podman.return_value = podman_images

        # Test when both Docker and Podman are available
        inventory = ContainerInventory("all")
        images = inventory.get_images()

        # Should have 2 images, one from each source
        self.assertEqual(len(images), 2)

        # First image should be Docker, second should be Podman
        self.assertEqual(images[0]["source"], "docker")
        self.assertEqual(images[1]["source"], "podman")

        # Test Docker only
        inventory = ContainerInventory("docker")
        images = inventory.get_images()

        # Should have 1 image from Docker
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["source"], "docker")

        # Test Podman only
        inventory = ContainerInventory("podman")
        images = inventory.get_images()

        # Should have 1 image from Podman
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["source"], "podman")

    def test_format_size(self):
        """Test formatting bytes to human-readable sizes."""
        # Use patch to avoid sys.exit when Docker/Podman aren't available
        with patch(
            "container_inventory.core.ContainerInventory._check_tool_availability",
            return_value=True,
        ):
            inventory = ContainerInventory()

            # Test various sizes
            self.assertEqual(inventory._format_size(500), "500.00B")
            self.assertEqual(inventory._format_size(1024), "1.00KB")
            self.assertEqual(inventory._format_size(1048576), "1.00MB")
            self.assertEqual(inventory._format_size(1073741824), "1.00GB")
            self.assertEqual(inventory._format_size(1099511627776), "1.00TB")

            # Test large number that would be in PB
            self.assertEqual(inventory._format_size(1125899906842624), "1.00PB")


if __name__ == "__main__":
    unittest.main()
