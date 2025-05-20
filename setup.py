from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="container-inventory",
    version="0.1.0",
    author="coopdloop",
    author_email="coopdevsec@proton.me",
    description="Docker and Podman container image inventory and vulnerability scanning tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coopdloop/oss-docker-podman-inv-scan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rich>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "container-inventory=container_inventory.cli:main",
            "container-inventory-create-test-images=container_inventory.create_test_images:main",
        ],
    },
)
