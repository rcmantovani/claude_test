from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="app-publisher",
    version="0.1.0",
    author="Your Name",
    description="A simple tool to publish Python web applications to remote servers via SSH",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/app-publisher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "app-publisher=app_publisher.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app_publisher": ["templates/*"],
    },
)
