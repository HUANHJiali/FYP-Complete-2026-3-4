"""
答辩演示一键校验脚本
执行顺序：
1) Django 配置检查
2) 四链路回归基线（登录/考试/练习/AI评分）
3) 关键健康接口检查（无需启动 runserver）

用法：
  python tools/run_defense_demo_check.py
"""

import os
import subprocess
import sys


def run_step(name: str, cmd: list[str]) -> int:
    print(f"\n=== {name} ===")
    print("$", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"✅ {name} 通过")
    else:
        print(f"❌ {name} 失败（exit={result.returncode}）")
    return result.returncode


def check_health_endpoints() -> int:
    print("\n=== 健康接口检查（Django Test Client）===")

    # 保证可从 tools/ 目录正确导入 server.settings
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    import django
    django.setup()

    from django.test import Client

    client = Client()
    strict_health = os.getenv('STRICT_HEALTH', '0').strip() in ('1', 'true', 'True')

    failed = 0

    # 必须通过：轻量健康检查
    simple_resp = client.get('/api/health/simple/')
    if simple_resp.status_code == 200:
        print(f"✅ /api/health/simple/ -> {simple_resp.status_code}")
    else:
        print(f"❌ /api/health/simple/ -> {simple_resp.status_code} (expected 200)")
        failed += 1

    # 可选严格：完整健康检查（依赖数据库/外部服务）
    full_resp = client.get('/api/health/')
    if full_resp.status_code == 200:
        print(f"✅ /api/health/ -> {full_resp.status_code}")
    else:
        if strict_health:
            print(f"❌ /api/health/ -> {full_resp.status_code} (strict mode expected 200)")
            failed += 1
        else:
            print(f"⚠️ /api/health/ -> {full_resp.status_code}（依赖未就绪，非严格模式下仅告警）")

    if failed == 0:
        print("✅ 健康接口检查通过")
        return 0

    print(f"❌ 健康接口检查失败：{failed} 项")
    return 1


def main() -> int:
    steps = [
        ("Django 系统检查", [sys.executable, 'manage.py', 'check']),
        ("四链路回归基线", [sys.executable, 'tools/run_regression_baseline.py']),
    ]

    for name, cmd in steps:
        code = run_step(name, cmd)
        if code != 0:
            return code

    return check_health_endpoints()


if __name__ == '__main__':
    raise SystemExit(main())
