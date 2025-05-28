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
        with patch("sys.argv", ["container_inventory", "--type", "docker"]):
            args = setup_cli()
            self.assertEqual(args.type, "docker")
            self.assertFalse(args.append)
            self.assertIsNone(args.output)


        # Test with output option
        with patch("sys.argv", ["container_inventory", "--output", "output.json"]):
            args = setup_cli()
            self.assertEqual(args.output, "output.json")

        # Test with append option
        with patch("sys.argv", ["container_inventory", "--output", "output.json", "--append"]):
            args = setup_cli()
            self.assertTrue(args.append)


    @patch("container_inventory.cli.ContainerInventory")
    @patch("container_inventory.cli.setup_cli")
    def test_main(self, mock_setup_cli, mock_inventory_class):
        """Test main function."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.type = "all"
        mock_args.output = None
        mock_args.append = False

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



if __name__ == "__main__":
    unittest.main()
