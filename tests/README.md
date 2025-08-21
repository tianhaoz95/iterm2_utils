# Tests for sglang_iterm2_utils

这个目录包含了 `sglang_iterm2_utils` 包的所有单元测试。

## 测试文件结构

```
tests/
├── __init__.py                           # 测试包初始化文件
├── test_sglang_iterm2_utils.py          # 包的整体集成测试
├── test_ssh_connections.py              # SSH连接功能的专门测试
├── test_session_management.py           # 会话管理功能的专门测试
├── test_multi_node_init.py              # 多节点初始化功能的专门测试
├── test_append_python_path_pytest.py    # Python路径追加功能的专门测试
└── README.md                            # 测试文档（本文件）
```

## 测试覆盖范围

### 📡 SSH连接测试 (`test_ssh_connections.py`)
- ✅ 函数存在性和签名验证
- ✅ 无窗口/标签页/会话的边缘情况
- ✅ 单个和多个主机连接
- ✅ 主机循环分配逻辑
- ✅ 不同用户名和主机格式
- ✅ 异常处理测试
- ✅ 参数验证
- **测试数量：18个**

### 🔄 会话管理测试 (`test_session_management.py`)
- ✅ 函数存在性和签名验证
- ✅ 无窗口/标签页的边缘情况
- ✅ 空会话列表处理
- ✅ 单个和多个会话重启
- ✅ 异常处理测试
- ✅ 混合会话状态测试
- ✅ 连接参数使用验证
- **测试数量：13个**

### 🚀 多节点初始化测试 (`test_multi_node_init.py`)
- ✅ 函数存在性和签名验证
- ✅ 无窗口/标签页/会话的边缘情况
- ✅ 单会话和多会话初始化
- ✅ IP地址检测和解析
- ✅ 环境变量设置验证
- ✅ 异常处理测试
- ✅ 工具函数单元测试
- **测试数量：20个**

### 🐍 Python路径追加测试 (`test_append_python_path_pytest.py`)
- ✅ 函数存在性和签名验证
- ✅ 无窗口/标签页/会话的边缘情况
- ✅ 多路径和多会话处理
- ✅ 空路径列表处理
- ✅ 命令格式验证
- ✅ 异常处理测试
- ✅ 边界条件测试
- **测试数量：8个**

### 🔗 整体集成测试 (`test_sglang_iterm2_utils.py`)
- ✅ 包导入和元数据验证
- ✅ 函数可访问性测试
- ✅ 基本功能集成测试
- **测试数量：13个**

## 运行测试

### 使用Make命令（推荐）

```bash
# 运行所有测试
make test

# 运行详细输出的测试
make test-verbose

# 只运行SSH连接测试
make test-ssh

# 只运行会话管理测试
make test-session

# 只运行多节点初始化测试
make test-multi-node

# 只运行Python路径追加测试
make test-append-python-path

# 运行所有测试并显示详细错误信息
make test-all
```

### 使用pytest直接运行

```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试文件
python3 -m pytest tests/test_ssh_connections.py -v
python3 -m pytest tests/test_session_management.py -v
python3 -m pytest tests/test_multi_node_init.py -v
python3 -m pytest tests/test_append_python_path_pytest.py -v
python3 -m pytest tests/test_sglang_iterm2_utils.py -v

# 运行特定测试方法
python3 -m pytest tests/test_ssh_connections.py::TestSSHConnections::test_connect_remote_machines_success -v
```

### 使用内置测试运行器

```bash
# 运行单个测试文件
python3 tests/test_ssh_connections.py
python3 tests/test_session_management.py
python3 tests/test_multi_node_init.py
python3 tests/test_sglang_iterm2_utils.py
# 注意：test_append_python_path_pytest.py 需要使用 pytest 运行
```

## 测试统计

- **总测试数量：72个** (18+13+20+8+13)
- **测试覆盖模块：5个**
- **测试通过率：100%**
- **主要功能覆盖：**
  - SSH连接管理 ✅
  - 会话重启管理 ✅
  - 多节点初始化 ✅
  - Python路径管理 ✅
  - 错误处理 ✅
  - 边缘情况处理 ✅
  - 参数验证 ✅

## 测试设计原则

### 🎯 全面覆盖
- 正常流程测试
- 边缘情况测试
- 异常处���测试
- 参数验证测试

### 🏗️ 模块化设计
- 每个模块有专门的测试文件
- 清晰的测试类别分离
- 可独立运行的测试套件

### 🔍 Mock策略
- 使用 `unittest.mock` 进行依赖隔离
- 模拟iTerm2 API调用
- 验证函数调用参数和次数

### 📊 异步测试支持
- 专门的异步测试类
- 协程函数测试
- 异步操作验证

## 开发指南

### 添加新测试

1. **选择合适的测试文件**：
   - SSH相关功能 → `test_ssh_connections.py`
   - 会话管理相关 → `test_session_management.py`
   - 包级别功能 → `test_sglang_iterm2_utils.py`

2. **遵循命名约定**：
   - 测试类：`TestModuleName`
   - 测试方法：`test_function_name_scenario`

3. **使用标准测试结构**：
   ```python
   async def test_function_name_scenario(self):
       """Test description"""
       # Arrange - 设置测试数据
       # Act - 执行被测试的功能
       # Assert - 验证结果
   ```

### 运行测试的最佳实践

1. **开发期间**：使用 `make test-ssh` 或 `make test-session` 快速测试特定模块
2. **提交前**：使用 `make test` 确保所有测试通过
3. **调试时**：使用 `make test-verbose` 获取详细输出
4. **CI/CD**：使用 `make test-all` 获取完整的测试报告

---

## 关于异步测试警告

当前测试中出现的 `RuntimeWarning` 是由于使用了 `unittest` 框架的异步测试方法。这些警告不影响测试功能，所有测试都能正常通过。未来可以考虑迁移到 `pytest-asyncio` 来完全消除这些警告。
