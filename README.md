# iterm2_utils

A simple hello world utility package for iTerm2.

## Installation

You can install this package using pip:

```bash
# Install from local directory
pip install .

# Install in development mode
pip install -e .
```

## Usage

### Command Line

You can use the package in your Python code:
After installation, you can use the `iterm2-utils` command:

from iterm2_utils import hello_world
```bash
# Basic hello world
iterm2-utils

# Personalized greeting
iterm2-utils --name "Your Name"
iterm2-utils -n "Your Name"

# Show version
iterm2-utils --version
```

### Python API

You can also use the package in your Python code:

```python
from iterm2_utils import hello_world, hello_user

# Basic usage
print(hello_world())

# Personalized greeting
print(hello_user("Alice"))
```

## Development

To install in development mode:

```bash
pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
