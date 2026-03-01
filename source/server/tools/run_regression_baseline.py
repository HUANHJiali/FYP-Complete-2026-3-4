"""
运行P1回归基线（登录/考试/练习/AI评分）
用法：
  python tools/run_regression_baseline.py
"""

import subprocess
import sys


def main() -> int:
    labels = [
        'app.tests.test_regression_baseline.RegressionBaselineTest.test_login_flow',
        'app.tests.test_regression_baseline.RegressionBaselineTest.test_exam_flow',
        'app.tests.test_regression_baseline.RegressionBaselineTest.test_practice_flow',
        'app.tests.test_regression_baseline.RegressionBaselineTest.test_ai_scoring_flow',
    ]

    cmd = [sys.executable, 'manage.py', 'test'] + labels
    print('>>> Running regression baseline:')
    for label in labels:
        print(f'  - {label}')

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print('\n✅ Regression baseline passed')
    else:
        print('\n❌ Regression baseline failed')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
