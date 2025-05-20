"""
Tests for the CLI module of Container Inventory.
"""

import unittest
from unittest.mock import patch, MagicMock

from container_inventory.cli import setup_cli, main


class TestCLI(unittest.TestCase):
    """Tests for the CLI functions."""

    def test_setup_cli(self):
        """Test CLI argument setup."""
        # Mock sys.argv to test argument parsing
        with patch("sys.argv", ["container-inventory", "--type", "docker"]):
            args = setup_cli()
            self.assertEqual(args.type, "docker")
            self.assertFalse(args.scan)
            self.assertFalse(args.append)
            self.assertIsNone(args.output)
            self.assertIsNone(args.vulns_output)
            self.assertIsNone(args.image)

        # Test with scan option
        with patch("sys.argv", ["container-inventory", "--scan"]):
            args = setup_cli()
            self.assertEqual(args.type, "all")  # default value
            self.assertTrue(args.scan)

        # Test with output option
        with patch("sys.argv", ["container-inventory", "--output", "output.json"]):
            args = setup_cli()
            self.assertEqual(args.output, "output.json")

        # Test with append option
        with patch("sys.argv", ["container-inventory", "--output", "output.json", "--append"]):
            args = setup_cli()
            self.assertTrue(args.append)

        # Test with vulns-output
        with patch("sys.argv", ["container-inventory", "--scan", "--vulns-output", "vulns.json"]):
            args = setup_cli()
            self.assertTrue(args.scan)
            self.assertEqual(args.vulns_output, "vulns.json")

        # Test with image option
        with patch("sys.argv", ["container-inventory", "--scan", "--image", "test:latest"]):
            args = setup_cli()
            self.assertTrue(args.scan)
            self.assertEqual(args.image, "test:latest")

    @patch("container_inventory.cli.ContainerInventory")
    @patch("container_inventory.cli.setup_cli")
    def test_main(self, mock_setup_cli, mock_inventory_class):
        """Test main function."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.type = "all"
        mock_args.scan = False
        mock_args.output = None
        mock_args.append = False
        mock_args.vulns_output = None
        mock_args.image = None

        mock_setup_cli.return_value = mock_args

        mock_inventory = MagicMock()
        mock_inventory.get_images.return_value = [
            {"ID": "123", "Repository": "test", "Tag": "latest", "source": "docker"}
        ]
        mock_inventory_class.return_value = mock_inventory

        # Test basic inventory display
        main()

        # Verify inventory was created with the correct type
        mock_inventory_class.assert_called_with("all")

        # Verify images were retrieved
        mock_inventory.get_images.assert_called_once()

        # Verify inventory was displayed
        mock_inventory.display_inventory.assert_called_once()

        # Verify no scanning happened
        mock_inventory.scan_image_vulnerabilities.assert_not_called()

        # Reset mocks
        mock_inventory.reset_mock()
        mock_inventory_class.reset_mock()

        # Test with scan option
        mock_args.scan = True
        mock_inventory.trivy_available = True

        main()

        # Verify scan was called
        self.assertTrue(mock_inventory.scan_image_vulnerabilities.called)


if __name__ == "__main__":
    unittest.main()
