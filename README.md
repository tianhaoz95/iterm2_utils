# iterm2_utils

Utilities for iTerm2 automation and remote machine management.

## Installation

You can install this package using pip:

```bash
# Install from local directory
pip install .

# Install in development mode with test dependencies
pip install -e .[test]
```

## Usage

### Python API

```python
import iterm2
from iterm2_utils import connect_remote_machines, restart_all_sessions_in_current_tab

async def main(connection):
    # Connect to remote machines via SSH
    hosts = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
    await connect_remote_machines(connection, hosts, "username")

    # Restart all sessions in current tab
    await restart_all_sessions_in_current_tab(connection)

# Run with iTerm2
iterm2.run_until_complete(main)
```

## Project Structure

```
iterm2_utils/
├── iterm2_utils/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── ssh_connections.py  # SSH connection utilities
│   └── session_management.py # Session management utilities
├── tests/                  # Test package
│   ├── __init__.py
│   └── test_iterm2_utils.py # Unit tests
├── pytest.ini             # Pytest configuration
├── Makefile               # Development commands
└── setup.py               # Package setup
```

## Testing

我们为所有模块提供了全面的测试覆盖，包含44个测试用例。

### 快速运行测试

```bash
# 运行所有测试（推荐）
make test

# 运行特定模块的测试
make test-ssh      # SSH连接功能测试
make test-session  # 会话管理功能测试

# 详细输出
make test-verbose
make test-all      # 包含详细错误信息
```

### 使用pytest运行

```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试文件
python3 -m pytest tests/test_ssh_connections.py -v
python3 -m pytest tests/test_session_management.py -v
python3 -m pytest tests/test_iterm2_utils.py -v
```

### 测试覆盖详情

- **SSH连接测试**：18个测试用例，涵盖连接管理、错误处理、参数验证
- **会话管理测试**：13个测试用例，涵盖会话重启、异常处理、边缘情况
- **集成测试**：13个测试用例，涵盖包级别功能和导入验证
- **总计**：44个测试用例，100%通过率

更多测试详情请查看 [`tests/README.md`](tests/README.md)。

## Development

To set up for development:

```bash
# Install in development mode with test dependencies
pip install -e .[test]

# Run tests
make test

# Clean build artifacts
make clean
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
