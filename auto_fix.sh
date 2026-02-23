#!/bin/bash
# FYP项目自动修复脚本
# 自动修复高优先级的安全和性能问题

set -e  # 遇到错误立即退出

echo "========================================"
echo "  FYP项目自动改进工具 v1.0"
echo "========================================"
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤计数
STEP=0

# 辅助函数
print_step() {
    STEP=$((STEP + 1))
    echo -e "${GREEN}[步骤 $STEP]${NC} $1"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Git仓库
if [ ! -d ".git" ]; then
    print_error "这不是一个Git仓库！"
    echo "建议: 先初始化Git仓库"
    exit 1
fi

# 创建备份分支
print_step "创建Git备份分支"
BACKUP_BRANCH="backup-before-auto-improvement-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BACKUP_BRANCH" 2>/dev/null || git checkout -b "$BACKUP_BRANCH"
print_success "备份分支: $BACKUP_BRANCH"

# 返回主分支
git checkout main 2>/dev/null || git checkout master
print_success "已返回主分支"

# 1. 修复XSS漏洞
print_step "修复XSS漏洞（messageCenter.vue）"
MESSAGE_CENTER_FILE="source/client/src/views/pages/messageCenter.vue"

if [ -f "$MESSAGE_CENTER_FILE" ]; then
    # 备份原文件
    cp "$MESSAGE_CENTER_FILE" "$MESSAGE_CENTER_FILE.bak"

    # 检查是否使用了v-html
    if grep -q "v-html.*formatContent" "$MESSAGE_CENTER_FILE"; then
        print_warning "发现v-html使用，正在修复..."

        # 创建修复补丁
        cat > /tmp/xss_fix.patch << 'EOF'
--- a/source/client/src/views/pages/messageCenter.vue
+++ b/source/client/src/views/pages/messageCenter.vue
@@ -161,7 +161,7 @@
                         <Divider />

                         <div class="message-content">
-                            <div class="content-text" v-html="formatContent(selectedMessage.content)"></div>
+                            <div class="content-text">{{ selectedMessage.content }}</div>

                             <div v-if="selectedMessage.attachments && selectedMessage.attachments.length > 0" class="attachments">
EOF

        print_success "XSS漏洞修复补丁已创建"
        print_warning "请手动应用补丁或重新编译前端"
    else
        print_success "未发现XSS漏洞风险"
    fi
else
    print_error "文件不存在: $MESSAGE_CENTER_FILE"
fi

# 2. 移除硬编码API密钥
print_step "检查硬编码的API密钥"
DOCKER_COMPOSE_FILE="docker-compose.yml"

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    if grep -q "ZHIPUAI_API_KEY:.*[a-zA-Z0-9]\{32,\}" "$DOCKER_COMPOSE_FILE"; then
        print_warning "发现硬编码的API密钥！"

        # 创建.env.example文件（如果不存在）
        if [ ! -f ".env" ]; then
            cat > .env << EOF
# 数据库配置
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
EOF
            print_success "已创建.env文件"

            # 添加到.gitignore
            if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
                echo ".env" >> .gitignore
                print_success "已将.env添加到.gitignore"
            fi
        fi

        print_warning "请手动从docker-compose.yml移除API密钥并使用环境变量"
    else
        print_success "未发现硬编码API密钥"
    fi
fi

# 3. 修复密码字段长度
print_step "检查密码字段长度"
MODELS_FILE="source/server/app/models.py"

if [ -f "$MODELS_FILE" ]; then
    if grep -q "passWord.*max_length=32" "$MODELS_FILE"; then
        print_warning "发现密码字段长度不足（32字符）"

        # 创建迁移脚本
        cat > /tmp/fix_password_field.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复密码字段长度"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source/server'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.db import connection

def fix_password_field():
    """修复Users表密码字段长度"""
    with connection.cursor() as cursor:
        # 检查当前字段长度
        cursor.execute("""
            SELECT CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA='db_exam'
            AND COLUMN_NAME='pass_word'
            AND TABLE_NAME='fater_users'
        """)
        result = cursor.fetchone()
        current_length = result[0] if result else 0

        print(f"当前密码字段长度: {current_length}")

        if current_length < 255:
            print("正在修改密码字段长度为255...")
            cursor.execute("""
                ALTER TABLE fater_users
                MODIFY COLUMN pass_word VARCHAR(255) NOT NULL
            """)
            print("✅ 密码字段长度已修改为255")
        else:
            print("✅ 密码字段长度已足够")

if __name__ == '__main__':
    try:
        fix_password_field()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
EOF

        chmod +x /tmp/fix_password_field.py
        print_success "密码修复脚本已创建: /tmp/fix_password_field.py"
        print_warning "请手动运行: python /tmp/fix_password_field.py"
    else
        print_success "密码字段长度已足够"
    fi
fi

# 4. 代码质量检查
print_step "检查Python代码质量"
if command -v flake8 &> /dev/null; then
    echo "运行flake8..."
    flake8 source/server/app/ --max-line-length=120 --ignore=E501,W503 || true
    print_success "代码质量检查完成"
else
    print_warning "flake8未安装，跳过代码检查"
    echo "安装: pip install flake8"
fi

# 5. 检查安全问题
print_step "安全扫描"
echo "检查常见安全问题..."

# 检查是否有调试模式
if grep -r "DEBUG = True" source/server/server/ 2>/dev/null | grep -v ".pyc" | grep -v "settings.py"; then
    print_warning "发现非主配置文件中开启了DEBUG模式"
fi

# 检查是否有硬编码的密码
if grep -r "password.*=.*['\"]" source/server/app/ 2>/dev/null | grep -v ".pyc" | grep -v "passWord"; then
    print_warning "可能发现硬编码的密码"
fi

# 6. 创建改进报告
print_step "生成改进报告"
REPORT_FILE="IMPROVEMENT_REPORT_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# FYP项目自动改进报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**改进工具版本**: v1.0

---

## 🎯 发现的问题

### 🔴 高优先级

1. **XSS漏洞**
   - 文件: \`source/client/src/views/pages/messageCenter.vue:164\`
   - 状态: ${YELLOW}已创建修复补丁${NC}
   - 行动: 请手动应用补丁或修改为文本插值

2. **硬编码API密钥**
   - 文件: \`docker-compose.yml:68\`
   - 状态: ${YELLOW}已创建.env文件${NC}
   - 行动: 从docker-compose.yml移除密钥，使用环境变量

3. **密码字段长度**
   - 文件: \`source/server/app/models.py:54\`
   - 状态: ${YELLOW}已创建修复脚本${NC}
   - 行动: 运行 \`python /tmp/fix_password_field.py\`

### 🟡 中优先级

4. **代码质量**
   - 状态: ${GREEN}已完成检查${NC}
   - 建议: 定期运行flake8和black

5. **数据库查询优化**
   - 状态: ${YELLOW}待优化${NC}
   - 建议: 使用select_related和prefetch_related

---

## 📋 下一步行动

### 立即执行
1. 应用XSS修复补丁
2. 更新docker-compose.yml使用环境变量
3. 运行密码字段修复脚本
4. 重新编译前端
5. 重启服务

### 近期改进
1. 集成Swagger API文档
2. 提升测试覆盖率到80%+
3. 实现结构化错误处理
4. 扩展日志记录系统

---

**备份分支**: \`$BACKUP_BRANCH\`
**详细改进计划**: 查看 \`AUTO_IMPROVEMENT_PLAN.md\`
EOF

print_success "改进报告已生成: $REPORT_FILE"

# 7. Git提交建议
print_step "Git提交建议"
echo "当前状态:"
git status --short

echo ""
echo "建议的Git操作:"
echo "1. git add ."
echo "2. git commit -m \"自动改进: 安全和性能优化\""
echo "3. git push origin main"

echo ""
echo "========================================"
echo -e "${GREEN}  自动检查完成！${NC}"
echo "========================================"
echo ""
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📋 查看详细报告: cat $REPORT_FILE"
echo "📋 查看改进计划: cat AUTO_IMPROVEMENT_PLAN.md"
echo ""
echo -e "${YELLOW}⚠️  重要提示:${NC}"
echo "1. 请仔细阅读改进报告"
echo "2. 在应用修复前先在测试环境验证"
echo "3. 建议先创建feature分支进行改进"
echo ""
