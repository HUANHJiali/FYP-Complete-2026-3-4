#!/bin/bash
set -e

echo "等待 MySQL 数据库启动..."
# 等待 MySQL 就绪
while ! nc -z db 3306; do
  sleep 0.1
done
echo "MySQL 已就绪"

echo "运行数据库迁移..."
python manage.py migrate --noinput

echo "收集静态文件..."
python manage.py collectstatic --noinput --clear || true

echo "创建超级用户（如果不存在）..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123456')
    print("创建管理员账户: admin / 123456")
else:
    print("管理员账户已存在")
EOF

echo "初始化默认用户账户（admin/teacher/student）..."
python init_default_users.py || echo "默认用户初始化失败或已存在"

echo "启动 Django 服务器..."
python manage.py runserver 0.0.0.0:8000
