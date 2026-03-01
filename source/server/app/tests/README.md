## 测试说明

本目录包含后端单元测试与集成测试。

## P1 回归基线（推荐）

覆盖四条主链路：
- 登录
- 考试
- 练习
- AI评分

运行方式：

```bash
cd source/server
python tools/run_regression_baseline.py
```

或直接执行单文件：

```bash
cd source/server
python manage.py test app.tests.test_regression_baseline
```

## 说明

- 测试环境默认使用内存 SQLite（`settings.py` 中 `IS_TESTING` 逻辑）。
- AI评分链路只校验接口可用与响应结构，不依赖真实外部 API 可用性。
