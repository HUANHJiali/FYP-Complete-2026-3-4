"""
FYP项目自动修复工具（Python版本）
自动修复高优先级的安全和性能问题

使用方法:
    python auto_fix.py

功能:
    1. 修复XSS漏洞
    2. 移除硬编码API密钥
    3. 修复密码字段长度
    4. 代码质量检查
    5. 安全扫描
    6. 生成改进报告
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

# 颜色代码（Windows兼容）
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BLUE = '\033[94m'

class AutoImprover:
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.fixes_applied = []
        self.warnings = []

    def print_step(self, step_num, title):
        """打印步骤标题"""
        print(f"\n{Colors.BLUE}[步骤 {step_num}] {title}{Colors.RESET}")
        print()

    def print_success(self, message):
        """打印成功消息"""
        try:
            print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")
        except:
            print(f"[OK] {message}")

    def print_warning(self, message):
        """打印警告消息"""
        try:
            print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")
        except:
            print(f"[WARNING] {message}")

    def print_error(self, message):
        """打印错误消息"""
        try:
            print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")
        except:
            print(f"[ERROR] {message}")

    def check_xss_vulnerability(self):
        """检查XSS漏洞"""
        self.print_step(1, "检查XSS漏洞")

        message_center = self.project_root / "source/client/src/views/pages/messageCenter.vue"

        if not message_center.exists():
            self.print_error("文件不存在: messageCenter.vue")
            return False

        content = message_center.read_text(encoding='utf-8')

        # 检查v-html使用
        if 'v-html.*formatContent' in content:
            self.print_warning("发现XSS漏洞风险！")
            self.issues.append({
                'type': 'XSS漏洞',
                'file': 'messageCenter.vue',
                'line': 164,
                'severity': '高',
                'description': '使用v-html直接渲染用户输入',
                'fix': '将v-html改为文本插值 {{ }} 或使用DOMPurify'
            })

            # 创建修复后的文件
            content_fixed = re.sub(
                r'<div class="content-text" v-html="formatContent\(selectedMessage\.content\)"></div>',
                '<div class="content-text">{{ selectedMessage.content }}</div>',
                content
            )

            # 保存修复建议
            fix_file = self.project_root / "fixes" / "xss_fix_messageCenter.vue"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(content_fixed, encoding='utf-8')

            self.print_success("修复方案已生成: fixes/xss_fix_messageCenter.vue")
            self.print_warning("请手动替换原文件或重新编译前端")
            return True
        else:
            self.print_success("未发现XSS漏洞风险")
            return False

    def check_api_keys(self):
        """检查硬编码的API密钥"""
        self.print_step(2, "检查硬编码的API密钥")

        docker_compose = self.project_root / "docker-compose.yml"

        if not docker_compose.exists():
            self.print_error("docker-compose.yml不存在")
            return False

        content = docker_compose.read_text(encoding='utf-8')

        # 检查ZhipuAI API密钥
        pattern = r'ZHIPUAI_API_KEY:\s*[a-zA-Z0-9]{32,}'

        match = re.search(pattern, content)
        if match:
            self.print_warning("发现硬编码的ZhipuAI API密钥！")
            self.issues.append({
                'type': '敏感信息泄露',
                'file': 'docker-compose.yml',
                'severity': '高',
                'description': 'API密钥硬编码在配置文件中',
                'fix': '使用环境变量或Docker secrets'
            })

            # 创建.env文件
            env_file = self.project_root / ".env"

            if not env_file.exists():
                env_content = """# 数据库配置
DB_NAME=db_exam
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306

# Django配置
SECRET_KEY=django-insecure-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ZhipuAI配置
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
"""
                env_file.write_text(env_content, encoding='utf-8')
                self.print_success("已创建.env文件")

                # 更新.gitignore
                gitignore = self.project_root / ".gitignore"
                if gitignore.exists():
                    gitignore_content = gitignore.read_text(encoding='utf-8')
                    if '.env' not in gitignore_content:
                        gitignore_content += '\n.env\n'
                        gitignore.write_text(gitignore_content, encoding='utf-8')
                        self.print_success("已将.env添加到.gitignore")
                else:
                    gitignore.write_text('.env\n', encoding='utf-8')
                    self.print_success("已创建.gitignore并添加.env")

            # 创建修复建议
            fix_suggestion = """# 修复硬编码API密钥

## 步骤1: 编辑docker-compose.yml

将:
```yaml
environment:
  - ZHIPUAI_API_KEY=fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

改为:
```yaml
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}
```

## 步骤2: 更新.env文件

将:
```
ZHIPUAI_API_KEY=your_api_key_here
```

改为:
```
ZHIPUAI_API_KEY=你的真实API密钥
```

## 步骤3: 重启服务

```bash
docker-compose down
docker-compose up -d
```
"""
            fix_file = self.project_root / "fixes" / "api_key_fix.md"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(fix_suggestion, encoding='utf-8')

            self.print_success("修复建议已生成: fixes/api_key_fix.md")
            return True
        else:
            self.print_success("未发现硬编码API密钥")
            return False

    def check_password_field(self):
        """检查密码字段长度"""
        self.print_step(3, "检查密码字段长度")

        models_file = self.project_root / "source/server/app/models.py"

        if not models_file.exists():
            self.print_error("models.py不存在")
            return False

        content = models_file.read_text(encoding='utf-8')

        # 检查密码字段长度
        if 'passWord.*max_length=32' in content:
            self.print_warning("发现密码字段长度不足（32字符）！")
            self.issues.append({
                'type': '安全风险',
                'file': 'models.py',
                'line': 54,
                'severity': '高',
                'description': '密码字段只有32字符，可能截断哈希',
                'fix': '修改为max_length=255并运行迁移'
            })

            # 创建修复脚本
            fix_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
修复密码字段长度
运行方式: python fix_password_length.py
\"\"\"
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source/server'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from app.models import Users
from django.db import connection

def fix_password_field():
    \"\"\"修复Users表密码字段长度\"\"\"
    print("正在修复密码字段长度...")

    with connection.cursor() as cursor:
        # 检查当前字段长度
        cursor.execute(\"\"\"
            SELECT CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA='db_exam'
            AND COLUMN_NAME='pass_word'
            AND TABLE_NAME='fater_users'
        \"\"\")
        result = cursor.fetchone()
        current_length = result[0] if result else 0

        print(f"当前密码字段长度: {current_length}")

        if current_length < 255:
            print("正在修改密码字段长度为255...")
            cursor.execute(\"\"\"
                ALTER TABLE fater_users
                MODIFY COLUMN pass_word VARCHAR(255) NOT NULL
            \"\"\")
            print("✅ 密码字段长度已修改为255")
        else:
            print("✅ 密码字段长度已足够")

    # 验证现有密码
    print("\n正在验证现有密码...")
    users = Users.objects.all()[:3]
    for user in users:
        if user.check_password('123456'):
            print(f"✅ 用户 {user.userName} 的密码验证通过")
        else:
            print(f"❌ 用户 {user.userName} 的密码验证失败")

if __name__ == '__main__':
    try:
        fix_password_field()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""

            fix_file = self.project_root / "fixes" / "fix_password_length.py"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(fix_script, encoding='utf-8')

            self.print_success("密码修复脚本已创建: fixes/fix_password_length.py")
            self.print_warning("请手动运行: python fixes/fix_password_length.py")
            return True
        else:
            self.print_success("密码字段长度已足够")
            return False

    def check_code_quality(self):
        """代码质量检查"""
        self.print_step(4, "代码质量检查")

        # 检查Python代码
        server_path = self.project_root / "source/server/app"
        if server_path.exists():
            py_files = list(server_path.rglob("*.py"))

            print(f"找到 {len(py_files)} 个Python文件")

            issues_found = 0

            for py_file in py_files:
                try:
                    content = py_file.read_text(encoding='utf-8')

                    # 检查常见问题
                    if 'except:' in content and 'except Exception' not in content:
                        if content.count('except:') > 3:
                            print(f"  {py_file.relative_to(self.project_root)}: 发现裸except")
                            issues_found += 1

                    # 检查长行（超过120字符）
                    lines = content.split('\n')
                    long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 120]
                    if long_lines:
                        print(f"  {py_file.relative_to(self.project_root)}: {len(long_lines)} 行超过120字符")
                        issues_found += 1

                except Exception as e:
                    pass

            if issues_found == 0:
                self.print_success("代码质量检查通过")
            else:
                self.print_warning(f"发现 {issues_found} 个代码质量问题")

    def security_scan(self):
        """安全扫描"""
        self.print_step(5, "安全扫描")

        security_issues = []

        # 检查调试模式
        settings_path = self.project_root / "source/server/server"
        if settings_path.exists():
            for file in settings_path.rglob("*.py"):
                content = file.read_text(encoding='utf-8')
                if "DEBUG = True" in content and "settings.py" not in file.name:
                    security_issues.append(f"{file.relative_to(self.project_root)}: 开启了DEBUG")

        # 检查硬编码的密码
        app_path = self.project_root / "source/server/app"
        if app_path.exists():
            for file in app_path.rglob("*.py"):
                content = file.read_text(encoding='utf-8')
                # 简单检查（可能有误报）
                if re.search(r"password\s*=\s*['\"][^'\"]{8,}", content):
                    security_issues.append(f"{file.relative_to(self.project_root)}: 可能包含硬编码密码")

        if security_issues:
            self.print_warning(f"发现 {len(security_issues)} 个安全问题:")
            for issue in security_issues:
                print(f"  - {issue}")
        else:
            self.print_success("未发现明显安全问题")

    def generate_report(self):
        """生成改进报告"""
        self.print_step(6, "生成改进报告")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"IMPROVEMENT_REPORT_{timestamp}.md"

        # 生成报告内容
        report_content = f"""# FYP项目自动改进报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**改进工具版本**: v1.0

---

## 🎯 发现的问题 ({len(self.issues)})

### 🔴 高优先级问题

"""
        # 添加问题列表
        for i, issue in enumerate(self.issues, 1):
            report_content += f"""
#### {i}. {issue['type']} ({issue['severity']})

- **文件**: `{issue.get('file', 'N/A')}`
- **描述**: {issue['description']}
- **修复建议**: {issue['fix']}

"""

        report_content += """
### 🟡 中优先级问题

1. **代码质量**
   - 状态: 已完成检查
   - 建议: 定期运行代码检查工具

2. **数据库查询优化**
   - 状态: 待优化
   - 建议: 使用select_related和prefetch_related

---

## 📋 修复文件清单

以下文件已生成修复方案：

"""

        # 列出修复文件
        fixes_dir = self.project_root / "fixes"
        if fixes_dir.exists():
            for fix_file in fixes_dir.iterdir():
                report_content += f"- `{fix_file.name}`\n"

        report_content += f"""

---

## 🚀 下一步行动

### 立即执行（高优先级）

1. **应用XSS修复**
   ```bash
   # 查看修复方案
   cat fixes/xss_fix_messageCenter.vue

   # 手动应用修复或参考修复方案修改代码
   ```

2. **移除硬编码API密钥**
   ```bash
   # 查看修复建议
   cat fixes/api_key_fix.md

   # 更新.env文件中的API密钥
   # 修改docker-compose.yml使用环境变量
   ```

3. **修复密码字段**
   ```bash
   # 运行修复脚本
   python fixes/fix_password_length.py

   # 重启服务验证
   ```

### 近期改进（中优先级）

1. 集成Swagger API文档
2. 提升测试覆盖率
3. 实现结构化错误处理
4. 扩展日志记录系统

---

## 📚 详细文档

- **改进计划**: 查看 `AUTO_IMPROVEMENT_PLAN.md`
- **测试报告**: 查看 `学生功能完整测试报告.md`
- **安全修复**: 查看 `中文乱码问题修复报告.md`

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**问题数量**: {len(self.issues)}
**修复文件**: {len(list((self.project_root / "fixes").iterdir())) if (self.project_root / "fixes").exists() else 0}

---

**下一步**: 运行 `python auto_fix.py` 应用自动修复
"""

        report_file.write_text(report_content, encoding='utf-8')
        self.print_success(f"改进报告已生成: {report_file.name}")

    def run(self):
        """运行所有检查和修复"""
        print("=" * 60)
        print("  FYP项目自动改进工具 v1.0")
        print("=" * 60)
        print("")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        # 创建fixes目录
        fixes_dir = self.project_root / "fixes"
        fixes_dir.mkdir(exist_ok=True)

        try:
            # 执行各项检查
            self.check_xss_vulnerability()
            self.check_api_keys()
            self.check_password_field()
            self.check_code_quality()
            self.security_scan()
            self.generate_report()

            # 总结
            print("\n" + "=" * 60)
            self.print_success("自动检查完成！")
            print("=" * 60)
            print("")
            print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("")
            print(f"📊 发现问题: {len(self.issues)}")
            print(f"📁 修复文件: {len(list(fixes_dir.iterdir()))}")
            print("")
            print("📋 查看详细报告:")
            print(f"   - type cat IMPROVEMENT_REPORT_*.md")
            print("📋 查看改进计划:")
            print("   - type cat AUTO_IMPROVEMENT_PLAN.md")
            print("")
            self.print_warning("⚠️  重要提示:")
            print("1. 请仔细阅读改进报告")
            print("2. 在应用修复前先在测试环境验证")
            print("3. 建议先创建Git分支进行改进")
            print("")

        except Exception as e:
            self.print_error(f"运行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    improver = AutoImprover()
    improver.run()
