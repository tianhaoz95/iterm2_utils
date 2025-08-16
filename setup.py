from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="iterm2-utils",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Utilities for iTerm2 automation and remote machine management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/iterm2_utils",
    packages=find_packages(),
    install_requires=[
        "iterm2>=2.7",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: macOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Terminals",
    ],
    python_requires=">=3.7",
)
