"""
FYP椤圭洰鑷姩淇宸ュ叿锛圥ython鐗堟湰锛?
鑷姩淇楂樹紭鍏堢骇鐨勫畨鍏ㄥ拰鎬ц兘闂

浣跨敤鏂规硶:
    python auto_fix.py

鍔熻兘:
    1. 淇XSS婕忔礊
    2. 绉婚櫎纭紪鐮丄PI瀵嗛挜
    3. 淇瀵嗙爜瀛楁闀垮害
    4. 浠ｇ爜璐ㄩ噺妫€鏌?
    5. 瀹夊叏鎵弿
    6. 鐢熸垚鏀硅繘鎶ュ憡
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

# 棰滆壊浠ｇ爜锛圵indows鍏煎锛?
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
        """鎵撳嵃姝ラ鏍囬"""
        print(f"\n{Colors.BLUE}[姝ラ {step_num}] {title}{Colors.RESET}")
        print()

    def print_success(self, message):
        """鎵撳嵃鎴愬姛娑堟伅"""
        try:
            print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")
        except:
            print(f"[OK] {message}")

    def print_warning(self, message):
        """鎵撳嵃璀﹀憡娑堟伅"""
        try:
            print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")
        except:
            print(f"[WARNING] {message}")

    def print_error(self, message):
        """鎵撳嵃閿欒娑堟伅"""
        try:
            print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")
        except:
            print(f"[ERROR] {message}")

    def check_xss_vulnerability(self):
        """妫€鏌SS婕忔礊"""
        self.print_step(1, "妫€鏌SS婕忔礊")

        message_center = self.project_root / "source/client/src/views/pages/messageCenter.vue"

        if not message_center.exists():
            self.print_error("鏂囦欢涓嶅瓨鍦? messageCenter.vue")
            return False

        content = message_center.read_text(encoding='utf-8')

        # 妫€鏌-html浣跨敤
        if 'v-html.*formatContent' in content:
            self.print_warning("鍙戠幇XSS婕忔礊椋庨櫓锛?)
            self.issues.append({
                'type': 'XSS婕忔礊',
                'file': 'messageCenter.vue',
                'line': 164,
                'severity': '楂?,
                'description': '浣跨敤v-html鐩存帴娓叉煋鐢ㄦ埛杈撳叆',
                'fix': '灏唙-html鏀逛负鏂囨湰鎻掑€?{{ }} 鎴栦娇鐢―OMPurify'
            })

            # 鍒涘缓淇鍚庣殑鏂囦欢
            content_fixed = re.sub(
                r'<div class="content-text" v-html="formatContent\(selectedMessage\.content\)"></div>',
                '<div class="content-text">{{ selectedMessage.content }}</div>',
                content
            )

            # 淇濆瓨淇寤鸿
            fix_file = self.project_root / "fixes" / "xss_fix_messageCenter.vue"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(content_fixed, encoding='utf-8')

            self.print_success("淇鏂规宸茬敓鎴? fixes/xss_fix_messageCenter.vue")
            self.print_warning("璇锋墜鍔ㄦ浛鎹㈠師鏂囦欢鎴栭噸鏂扮紪璇戝墠绔?)
            return True
        else:
            self.print_success("鏈彂鐜癤SS婕忔礊椋庨櫓")
            return False

    def check_api_keys(self):
        """妫€鏌ョ‖缂栫爜鐨凙PI瀵嗛挜"""
        self.print_step(2, "妫€鏌ョ‖缂栫爜鐨凙PI瀵嗛挜")

        docker_compose = self.project_root / "docker-compose.yml"

        if not docker_compose.exists():
            self.print_error("docker-compose.yml涓嶅瓨鍦?)
            return False

        content = docker_compose.read_text(encoding='utf-8')

        # 妫€鏌hipuAI API瀵嗛挜
        pattern = r'ZHIPUAI_API_KEY:\s*[a-zA-Z0-9]{32,}'

        match = re.search(pattern, content)
        if match:
            self.print_warning("鍙戠幇纭紪鐮佺殑ZhipuAI API瀵嗛挜锛?)
            self.issues.append({
                'type': '鏁忔劅淇℃伅娉勯湶',
                'file': 'docker-compose.yml',
                'severity': '楂?,
                'description': 'API瀵嗛挜纭紪鐮佸湪閰嶇疆鏂囦欢涓?,
                'fix': '浣跨敤鐜鍙橀噺鎴朌ocker secrets'
            })

            # 鍒涘缓.env鏂囦欢
            env_file = self.project_root / ".env"

            if not env_file.exists():
                env_content = """# 鏁版嵁搴撻厤缃?
DB_NAME=db_exam
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306

# Django閰嶇疆
SECRET_KEY=django-insecure-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ZhipuAI閰嶇疆
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
"""
                env_file.write_text(env_content, encoding='utf-8')
                self.print_success("宸插垱寤?env鏂囦欢")

                # 鏇存柊.gitignore
                gitignore = self.project_root / ".gitignore"
                if gitignore.exists():
                    gitignore_content = gitignore.read_text(encoding='utf-8')
                    if '.env' not in gitignore_content:
                        gitignore_content += '\n.env\n'
                        gitignore.write_text(gitignore_content, encoding='utf-8')
                        self.print_success("宸插皢.env娣诲姞鍒?gitignore")
                else:
                    gitignore.write_text('.env\n', encoding='utf-8')
                    self.print_success("宸插垱寤?gitignore骞舵坊鍔?env")

            # 鍒涘缓淇寤鸿
            fix_suggestion = """# 淇纭紪鐮丄PI瀵嗛挜

## 姝ラ1: 缂栬緫docker-compose.yml

灏?
```yaml
environment:
  - ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY
```

鏀逛负:
```yaml
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}
```

## 姝ラ2: 鏇存柊.env鏂囦欢

灏?
```
ZHIPUAI_API_KEY=your_api_key_here
```

鏀逛负:
```
ZHIPUAI_API_KEY=浣犵殑鐪熷疄API瀵嗛挜
```

## 姝ラ3: 閲嶅惎鏈嶅姟

```bash
docker-compose down
docker-compose up -d
```
"""
            fix_file = self.project_root / "fixes" / "api_key_fix.md"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(fix_suggestion, encoding='utf-8')

            self.print_success("淇寤鸿宸茬敓鎴? fixes/api_key_fix.md")
            return True
        else:
            self.print_success("鏈彂鐜扮‖缂栫爜API瀵嗛挜")
            return False

    def check_password_field(self):
        """妫€鏌ュ瘑鐮佸瓧娈甸暱搴?""
        self.print_step(3, "妫€鏌ュ瘑鐮佸瓧娈甸暱搴?)

        models_file = self.project_root / "source/server/app/models.py"

        if not models_file.exists():
            self.print_error("models.py涓嶅瓨鍦?)
            return False

        content = models_file.read_text(encoding='utf-8')

        # 妫€鏌ュ瘑鐮佸瓧娈甸暱搴?
        if 'passWord.*max_length=32' in content:
            self.print_warning("鍙戠幇瀵嗙爜瀛楁闀垮害涓嶈冻锛?2瀛楃锛夛紒")
            self.issues.append({
                'type': '瀹夊叏椋庨櫓',
                'file': 'models.py',
                'line': 54,
                'severity': '楂?,
                'description': '瀵嗙爜瀛楁鍙湁32瀛楃锛屽彲鑳芥埅鏂搱甯?,
                'fix': '淇敼涓簃ax_length=255骞惰繍琛岃縼绉?
            })

            # 鍒涘缓淇鑴氭湰
            fix_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
淇瀵嗙爜瀛楁闀垮害
杩愯鏂瑰紡: python fix_password_length.py
\"\"\"
import os
import sys

# 娣诲姞椤圭洰璺緞
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source/server'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from app.models import Users
from django.db import connection

def fix_password_field():
    \"\"\"淇Users琛ㄥ瘑鐮佸瓧娈甸暱搴"\"\"
    print("姝ｅ湪淇瀵嗙爜瀛楁闀垮害...")

    with connection.cursor() as cursor:
        # 妫€鏌ュ綋鍓嶅瓧娈甸暱搴?
        cursor.execute(\"\"\"
            SELECT CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA='db_exam'
            AND COLUMN_NAME='pass_word'
            AND TABLE_NAME='fater_users'
        \"\"\")
        result = cursor.fetchone()
        current_length = result[0] if result else 0

        print(f"褰撳墠瀵嗙爜瀛楁闀垮害: {current_length}")

        if current_length < 255:
            print("姝ｅ湪淇敼瀵嗙爜瀛楁闀垮害涓?55...")
            cursor.execute(\"\"\"
                ALTER TABLE fater_users
                MODIFY COLUMN pass_word VARCHAR(255) NOT NULL
            \"\"\")
            print("鉁?瀵嗙爜瀛楁闀垮害宸蹭慨鏀逛负255")
        else:
            print("鉁?瀵嗙爜瀛楁闀垮害宸茶冻澶?)

    # 楠岃瘉鐜版湁瀵嗙爜
    print("\n姝ｅ湪楠岃瘉鐜版湁瀵嗙爜...")
    users = Users.objects.all()[:3]
    for user in users:
        if user.check_password('123456'):
            print(f"鉁?鐢ㄦ埛 {user.userName} 鐨勫瘑鐮侀獙璇侀€氳繃")
        else:
            print(f"鉂?鐢ㄦ埛 {user.userName} 鐨勫瘑鐮侀獙璇佸け璐?)

if __name__ == '__main__':
    try:
        fix_password_field()
    except Exception as e:
        print(f"鉂?閿欒: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""

            fix_file = self.project_root / "fixes" / "fix_password_length.py"
            fix_file.parent.mkdir(exist_ok=True)
            fix_file.write_text(fix_script, encoding='utf-8')

            self.print_success("瀵嗙爜淇鑴氭湰宸插垱寤? fixes/fix_password_length.py")
            self.print_warning("璇锋墜鍔ㄨ繍琛? python fixes/fix_password_length.py")
            return True
        else:
            self.print_success("瀵嗙爜瀛楁闀垮害宸茶冻澶?)
            return False

    def check_code_quality(self):
        """浠ｇ爜璐ㄩ噺妫€鏌?""
        self.print_step(4, "浠ｇ爜璐ㄩ噺妫€鏌?)

        # 妫€鏌ython浠ｇ爜
        server_path = self.project_root / "source/server/app"
        if server_path.exists():
            py_files = list(server_path.rglob("*.py"))

            print(f"鎵惧埌 {len(py_files)} 涓狿ython鏂囦欢")

            issues_found = 0

            for py_file in py_files:
                try:
                    content = py_file.read_text(encoding='utf-8')

                    # 妫€鏌ュ父瑙侀棶棰?
                    if 'except:' in content and 'except Exception' not in content:
                        if content.count('except:') > 3:
                            print(f"  {py_file.relative_to(self.project_root)}: 鍙戠幇瑁竐xcept")
                            issues_found += 1

                    # 妫€鏌ラ暱琛岋紙瓒呰繃120瀛楃锛?
                    lines = content.split('\n')
                    long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 120]
                    if long_lines:
                        print(f"  {py_file.relative_to(self.project_root)}: {len(long_lines)} 琛岃秴杩?20瀛楃")
                        issues_found += 1

                except Exception as e:
                    pass

            if issues_found == 0:
                self.print_success("浠ｇ爜璐ㄩ噺妫€鏌ラ€氳繃")
            else:
                self.print_warning(f"鍙戠幇 {issues_found} 涓唬鐮佽川閲忛棶棰?)

    def security_scan(self):
        """瀹夊叏鎵弿"""
        self.print_step(5, "瀹夊叏鎵弿")

        security_issues = []

        # 妫€鏌ヨ皟璇曟ā寮?
        settings_path = self.project_root / "source/server/server"
        if settings_path.exists():
            for file in settings_path.rglob("*.py"):
                content = file.read_text(encoding='utf-8')
                if "DEBUG = True" in content and "settings.py" not in file.name:
                    security_issues.append(f"{file.relative_to(self.project_root)}: 寮€鍚簡DEBUG")

        # 妫€鏌ョ‖缂栫爜鐨勫瘑鐮?
        app_path = self.project_root / "source/server/app"
        if app_path.exists():
            for file in app_path.rglob("*.py"):
                content = file.read_text(encoding='utf-8')
                # 绠€鍗曟鏌ワ紙鍙兘鏈夎鎶ワ級
                if re.search(r"password\s*=\s*['\"][^'\"]{8,}", content):
                    security_issues.append(f"{file.relative_to(self.project_root)}: 鍙兘鍖呭惈纭紪鐮佸瘑鐮?)

        if security_issues:
            self.print_warning(f"鍙戠幇 {len(security_issues)} 涓畨鍏ㄩ棶棰?")
            for issue in security_issues:
                print(f"  - {issue}")
        else:
            self.print_success("鏈彂鐜版槑鏄惧畨鍏ㄩ棶棰?)

    def generate_report(self):
        """鐢熸垚鏀硅繘鎶ュ憡"""
        self.print_step(6, "鐢熸垚鏀硅繘鎶ュ憡")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"IMPROVEMENT_REPORT_{timestamp}.md"

        # 鐢熸垚鎶ュ憡鍐呭
        report_content = f"""# FYP椤圭洰鑷姩鏀硅繘鎶ュ憡

**鐢熸垚鏃堕棿**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**鏀硅繘宸ュ叿鐗堟湰**: v1.0

---

## 馃幆 鍙戠幇鐨勯棶棰?({len(self.issues)})

### 馃敶 楂樹紭鍏堢骇闂

"""
        # 娣诲姞闂鍒楄〃
        for i, issue in enumerate(self.issues, 1):
            report_content += f"""
#### {i}. {issue['type']} ({issue['severity']})

- **鏂囦欢**: `{issue.get('file', 'N/A')}`
- **鎻忚堪**: {issue['description']}
- **淇寤鸿**: {issue['fix']}

"""

        report_content += """
### 馃煛 涓紭鍏堢骇闂

1. **浠ｇ爜璐ㄩ噺**
   - 鐘舵€? 宸插畬鎴愭鏌?
   - 寤鸿: 瀹氭湡杩愯浠ｇ爜妫€鏌ュ伐鍏?

2. **鏁版嵁搴撴煡璇紭鍖?*
   - 鐘舵€? 寰呬紭鍖?
   - 寤鸿: 浣跨敤select_related鍜宲refetch_related

---

## 馃搵 淇鏂囦欢娓呭崟

浠ヤ笅鏂囦欢宸茬敓鎴愪慨澶嶆柟妗堬細

"""

        # 鍒楀嚭淇鏂囦欢
        fixes_dir = self.project_root / "fixes"
        if fixes_dir.exists():
            for fix_file in fixes_dir.iterdir():
                report_content += f"- `{fix_file.name}`\n"

        report_content += f"""

---

## 馃殌 涓嬩竴姝ヨ鍔?

### 绔嬪嵆鎵ц锛堥珮浼樺厛绾э級

1. **搴旂敤XSS淇**
   ```bash
   # 鏌ョ湅淇鏂规
   cat fixes/xss_fix_messageCenter.vue

   # 鎵嬪姩搴旂敤淇鎴栧弬鑰冧慨澶嶆柟妗堜慨鏀逛唬鐮?
   ```

2. **绉婚櫎纭紪鐮丄PI瀵嗛挜**
   ```bash
   # 鏌ョ湅淇寤鸿
   cat fixes/api_key_fix.md

   # 鏇存柊.env鏂囦欢涓殑API瀵嗛挜
   # 淇敼docker-compose.yml浣跨敤鐜鍙橀噺
   ```

3. **淇瀵嗙爜瀛楁**
   ```bash
   # 杩愯淇鑴氭湰
   python fixes/fix_password_length.py

   # 閲嶅惎鏈嶅姟楠岃瘉
   ```

### 杩戞湡鏀硅繘锛堜腑浼樺厛绾э級

1. 闆嗘垚Swagger API鏂囨。
2. 鎻愬崌娴嬭瘯瑕嗙洊鐜?
3. 瀹炵幇缁撴瀯鍖栭敊璇鐞?
4. 鎵╁睍鏃ュ織璁板綍绯荤粺

---

## 馃摎 璇︾粏鏂囨。

- **鏀硅繘璁″垝**: 鏌ョ湅 `AUTO_IMPROVEMENT_PLAN.md`
- **娴嬭瘯鎶ュ憡**: 鏌ョ湅 `瀛︾敓鍔熻兘瀹屾暣娴嬭瘯鎶ュ憡.md`
- **瀹夊叏淇**: 鏌ョ湅 `涓枃涔辩爜闂淇鎶ュ憡.md`

---

**鐢熸垚鏃堕棿**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**闂鏁伴噺**: {len(self.issues)}
**淇鏂囦欢**: {len(list((self.project_root / "fixes").iterdir())) if (self.project_root / "fixes").exists() else 0}

---

**涓嬩竴姝?*: 杩愯 `python auto_fix.py` 搴旂敤鑷姩淇
"""

        report_file.write_text(report_content, encoding='utf-8')
        self.print_success(f"鏀硅繘鎶ュ憡宸茬敓鎴? {report_file.name}")

    def run(self):
        """杩愯鎵€鏈夋鏌ュ拰淇"""
        print("=" * 60)
        print("  FYP椤圭洰鑷姩鏀硅繘宸ュ叿 v1.0")
        print("=" * 60)
        print("")
        print(f"寮€濮嬫椂闂? {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        # 鍒涘缓fixes鐩綍
        fixes_dir = self.project_root / "fixes"
        fixes_dir.mkdir(exist_ok=True)

        try:
            # 鎵ц鍚勯」妫€鏌?
            self.check_xss_vulnerability()
            self.check_api_keys()
            self.check_password_field()
            self.check_code_quality()
            self.security_scan()
            self.generate_report()

            # 鎬荤粨
            print("\n" + "=" * 60)
            self.print_success("鑷姩妫€鏌ュ畬鎴愶紒")
            print("=" * 60)
            print("")
            print(f"瀹屾垚鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("")
            print(f"馃搳 鍙戠幇闂: {len(self.issues)}")
            print(f"馃搧 淇鏂囦欢: {len(list(fixes_dir.iterdir()))}")
            print("")
            print("馃搵 鏌ョ湅璇︾粏鎶ュ憡:")
            print(f"   - type cat IMPROVEMENT_REPORT_*.md")
            print("馃搵 鏌ョ湅鏀硅繘璁″垝:")
            print("   - type cat AUTO_IMPROVEMENT_PLAN.md")
            print("")
            self.print_warning("鈿狅笍  閲嶈鎻愮ず:")
            print("1. 璇蜂粩缁嗛槄璇绘敼杩涙姤鍛?)
            print("2. 鍦ㄥ簲鐢ㄤ慨澶嶅墠鍏堝湪娴嬭瘯鐜楠岃瘉")
            print("3. 寤鸿鍏堝垱寤篏it鍒嗘敮杩涜鏀硅繘")
            print("")

        except Exception as e:
            self.print_error(f"杩愯澶辫触: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    improver = AutoImprover()
    improver.run()

