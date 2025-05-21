"""
Container Image Inventory and Vulnerability Scanner

A comprehensive Docker and Podman container image inventory and vulnerability scanning tool.
"""

__version__ = "0.1.0"
__author__ = "coopdloop"
__email__ = "coopdevsec@proton.me"

from container_inventory.core import ContainerInventory, Colors

__all__ = ["ContainerInventory", "Colors"]
