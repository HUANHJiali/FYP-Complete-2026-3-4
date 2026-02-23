### Linux 生产部署速查（给组员）

本指南提供最小可行的生产部署步骤与可复制模板，适用于 Ubuntu/Debian。目标栈：Nginx + Gunicorn(Django) + MySQL + 构建后的前端静态站点。

---

## 1. 安装系统依赖
```bash
sudo apt update
sudo apt install -y git curl build-essential python3 python3-venv python3-dev \
  mysql-server libmysqlclient-dev nginx

# Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 防火墙（可选）
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 2. 目录结构与拉取代码
```bash
sudo mkdir -p /opt/app && sudo chown -R $USER:$USER /opt/app
cd /opt/app
git clone <仓库地址> FYP2025-main
cd FYP2025-main
cp env.example .env
```

在 `.env` 设置：
- 数据库：主机/端口/库名/用户/密码
- Django：`SECRET_KEY`、`DEBUG=0`、`ALLOWED_HOSTS=域名或IP`
- AI Key（每位用户需在官方平台注册并获取，项目为每位用户提供3个月AI使用）：
  - 推荐通过 `.env` 注入，示例：
    ```
    AI_PROVIDER=openai
    OPENAI_API_KEY=你的APIKey
    OPENAI_BASE_URL=https://api.openai.com/v1
    OPENAI_MODEL=gpt-3.5-turbo
    ```
  - 使用智谱AI时参考 `config/智谱AI配置.md` 并替换为对应变量

## 3. MySQL 初始化
```bash
sudo mysql -u root
```
MySQL 控制台执行（按需修改用户名/密码/库名）：
```sql
CREATE DATABASE exam_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'exam_user'@'localhost' IDENTIFIED BY 'StrongPassword!123';
GRANT ALL PRIVILEGES ON exam_db.* TO 'exam_user'@'localhost';
FLUSH PRIVILEGES;
```
可选：导入项目示例数据
```bash
mysql -u exam_user -p exam_db < database/db_exam.sql
```

## 4. 后端（Django）依赖与迁移
```bash
cd /opt/app/FYP2025-main/source/server
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 迁移与初始化
python manage.py migrate
python /opt/app/FYP2025-main/source/server/check_and_create_base_data.py || true
python /opt/app/FYP2025-main/source/server/init_practice_data.py || true

# 收集静态
export DJANGO_SETTINGS_MODULE=server.settings
python manage.py collectstatic --noinput
```

## 5. 前端构建
```bash
cd /opt/app/FYP2025-main/source/client
npm ci
npm run build
# 产物目录：/opt/app/FYP2025-main/source/client/dist
```
如需，确保前端 API 使用 `/api` 前缀（见 `source/client/src/api/index.js`）。

## 6. Gunicorn systemd 服务（模板）
保存为 `/etc/systemd/system/ai-exam.service`：
```ini
[Unit]
Description=AI Exam Django (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/app/FYP2025-main/source/server
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/app/FYP2025-main/.env
ExecStart=/opt/app/FYP2025-main/source/server/.venv/bin/gunicorn \
  --workers 3 \
  --bind 127.0.0.1:8001 \
  server.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
启用与启动：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-exam
sudo systemctl start ai-exam
sudo systemctl status ai-exam --no-pager
```

ASGI/WS 版本：将 `ExecStart` 替换为 uvicorn，并指向 `server.asgi:application`。

## 7. Nginx 站点（模板）
保存为 `/etc/nginx/sites-available/ai-exam`：
```nginx
server {
    listen 80;
    server_name your.domain.com;  # 修改为域名或服务器IP

    root /opt/app/FYP2025-main/source/client/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /opt/app/FYP2025-main/source/server/staticfiles/;
        access_log off;
        expires 30d;
    }

    # 如有媒体：
    # location /media/ {
    #     alias /opt/app/FYP2025-main/source/server/media/;
    # }

    client_max_body_size 20m;
}
```
启用与重载：
```bash
sudo ln -s /etc/nginx/sites-available/ai-exam /etc/nginx/sites-enabled/ai-exam
sudo nginx -t
sudo systemctl restart nginx
```

## 8. HTTPS（Certbot）
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com --redirect -m you@example.com --agree-tos -n
```

## 9. 备份脚本（模板）
保存为 `/usr/local/bin/backup_exam_db.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
DATE=$(date +%F_%H-%M-%S)
mysqldump -u exam_user -p'StrongPassword!123' exam_db | gzip > /var/backups/exam_db_$DATE.sql.gz
find /var/backups -name 'exam_db_*.sql.gz' -mtime +14 -delete
```
授权与定时：
```bash
sudo chmod +x /usr/local/bin/backup_exam_db.sh
echo "0 3 * * * root /usr/local/bin/backup_exam_db.sh" | sudo tee /etc/cron.d/backup_exam_db >/dev/null
```

## 10. 验收清单（冒烟）
- 能通过域名 HTTPS 访问首页
- 登录/注册/后台能打开
- 试卷创建、作答、评分流程可用
- AI 功能正常（参考 `docs/AI功能使用说明.md`）
- 日志无明显错误（`journalctl -u ai-exam -e`、`/var/log/nginx/error.log`）

---

提示：
- 如果前端不是以 `/api` 作为后端前缀，请相应调整 Nginx `location` 或前端 API 基址。
- 需要 WebSocket/ASGI 时使用 uvicorn 并配置 `server.asgi:application`。
- 首次上线建议先用 IP 验证无误，再切域名并申请证书。


