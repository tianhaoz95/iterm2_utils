# Testing append_python_path Module

本文档说明如何运行 `append_python_path.py` 模块的单元测试。

## 安装测试依赖

```bash
pip install -r test_requirements.txt
```

或者手动安装：

```bash
pip install pytest pytest-asyncio iterm2
```

## 运行测试

### 方法 1: 使用测试运行脚本

```bash
python run_tests.py
```

### 方法 2: 直接使用 pytest

```bash
pytest test_append_python_path_pytest.py -v
```

### 方法 3: 运行所有测试

```bash
pytest -v
```

## 测试覆盖

测试包含以下场景：

1. **成功场景**：多个路径和多个 sessions
2. **错误处理**：
   - 没有活动窗口
   - 没有活动标签页
   - 没有 sessions
3. **边界条件**：
   - 空路径列表
   - 单个路径单个 session
4. **命令格式**：验证导出命令的正确格式
5. **分发机制**：验证命令正确发送到所有 sessions

## 测试文件

- `test_append_python_path_pytest.py` - 主要的 pytest 风格测试文件
- `pytest.ini` - pytest 配置文件
- `run_tests.py` - 测试运行脚本
- `test_requirements.txt` - 测试依赖

## 注意事项

- 测试使用 mock 对象模拟 iTerm2 环境
- 所有测试都是异步的，使用 `@pytest.mark.asyncio` 装饰器
- 测试验证命令的确切格式和调用次数
