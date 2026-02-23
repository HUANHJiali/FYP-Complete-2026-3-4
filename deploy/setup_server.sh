#!/usr/bin/env bash
set -euo pipefail

# Intelligent Exam System - Linux one-click setup (Ubuntu 20.04/22.04+)
# This script prepares a production environment with Python venv, Gunicorn, Nginx,
# builds the Vue frontend, collects Django static files, and configures systemd.

# Usage:
#   sudo bash deploy/setup_server.sh \
#     --project-root /opt/FYP2025-main \
#     --domain your.domain.com \
#     --env-file /etc/exam/.env \
#     --db-import yes

PROJECT_ROOT=""
DOMAIN_NAME=""
ENV_FILE="/etc/exam/.env"
DB_IMPORT="no"
PYTHON_BIN="python3"
NODE_BIN="node"
NGINX_SITE_PATH="/etc/nginx/sites-available/exam.conf"
SYSTEMD_UNIT_PATH="/etc/systemd/system/exam-gunicorn.service"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"; shift 2 ;;
    --domain)
      DOMAIN_NAME="$2"; shift 2 ;;
    --env-file)
      ENV_FILE="$2"; shift 2 ;;
    --db-import)
      DB_IMPORT="$2"; shift 2 ;;
    --python)
      PYTHON_BIN="$2"; shift 2 ;;
    --node)
      NODE_BIN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$PROJECT_ROOT" || -z "$DOMAIN_NAME" ]]; then
  echo "Usage: sudo bash deploy/setup_server.sh --project-root /path/to/FYP2025-main --domain your.domain.com [--env-file /etc/exam/.env] [--db-import yes|no]"
  exit 1
fi

echo "[1/9] Updating apt and installing dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
  build-essential curl git \
  python3 python3-venv python3-pip \
  nginx \
  mysql-client \
  pkg-config libmysqlclient-dev

echo "[2/9] Ensuring environment file exists at $ENV_FILE ..."
mkdir -p "$(dirname "$ENV_FILE")"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$PROJECT_ROOT/env.example" "$ENV_FILE" || true
  echo "INFO: Created $ENV_FILE from env.example. Please edit secrets inside it."
fi
chmod 640 "$ENV_FILE"

echo "[3/9] Backend setup (venv, requirements, migrations, collectstatic)..."
cd "$PROJECT_ROOT/source/server"
${PYTHON_BIN} -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt gunicorn uvicorn

# Optional: fallback to PyMySQL if mysqlclient fails on certain distros
python - <<'PY'
import sys
try:
    import MySQLdb  # noqa
    print('mysqlclient available')
except Exception:
    print('mysqlclient missing, installing PyMySQL fallback...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pymysql'])
    with open('server/__init__.py', 'a', encoding='utf-8') as f:
        if 'pymysql.install_as_MySQLdb()' not in f.read():
            f.write('\nimport pymysql\npymysql.install_as_MySQLdb()\n')
PY

if [[ "$DB_IMPORT" == "yes" ]]; then
  echo "[3.1] Importing MySQL schema and sample data..."
  mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || true
  mysql -u root -p db_exam < "$PROJECT_ROOT/database/db_exam.sql"
  if [[ -f "$PROJECT_ROOT/database/init_practice_data.sql" ]]; then
    mysql -u root -p db_exam < "$PROJECT_ROOT/database/init_practice_data.sql" || true
  fi
else
  echo "[3.1] Skipping DB import; running Django migrations instead..."
  python manage.py migrate --noinput
fi

python manage.py collectstatic --noinput

echo "[4/9] Frontend build (Vue)..."
cd "$PROJECT_ROOT/source/client"
if ! command -v ${NODE_BIN} >/dev/null 2>&1; then
  echo "ERROR: Node.js is not installed. Install Node.js 16/18+ and re-run."
  exit 1
fi
npm ci || npm install
npm run build

echo "[5/9] Install Nginx site with gzip and proxy settings..."
cat > "$NGINX_SITE_PATH" <<NGINX
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    # Frontend
    root ${PROJECT_ROOT}/source/client/dist;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 256;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /static/ {
        alias /app/static/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        access_log off;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120;
        proxy_connect_timeout 60;
        client_max_body_size 20M;
    }
}
NGINX

ln -sf "$NGINX_SITE_PATH" /etc/nginx/sites-enabled/exam.conf
rm -f /etc/nginx/sites-enabled/default || true
nginx -t
systemctl restart nginx

echo "[6/9] Install systemd unit for Gunicorn..."
cat > "$SYSTEMD_UNIT_PATH" <<SYSTEMD
[Unit]
Description=Gunicorn for Intelligent Exam System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_ROOT}/source/server
EnvironmentFile=${ENV_FILE}
ExecStart=${PROJECT_ROOT}/source/server/.venv/bin/gunicorn server.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 3 --timeout 120 --graceful-timeout 30 --access-logfile /var/log/exam_gunicorn_access.log --error-logfile /var/log/exam_gunicorn_error.log
Restart=always

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable exam-gunicorn
systemctl restart exam-gunicorn

echo "[7/9] Permissions and SELinux/AppArmor notes..."
chown -R www-data:www-data "$PROJECT_ROOT/source/client/dist" || true

echo "[8/9] Final checks..."
systemctl status exam-gunicorn --no-pager || true
curl -I "http://127.0.0.1" || true

cat <<INFO

Setup finished.

- Edit env:        $ENV_FILE
- Test backend:    curl -I http://127.0.0.1:8000/
- Test frontend:   http://$DOMAIN_NAME/
- Logs:
  * Gunicorn access: /var/log/exam_gunicorn_access.log
  * Gunicorn error:  /var/log/exam_gunicorn_error.log
- Nginx site:      $NGINX_SITE_PATH
- systemd unit:    $SYSTEMD_UNIT_PATH

Enable HTTPS with certbot:
  sudo apt-get install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d $DOMAIN_NAME

INFO

echo "[9/9] Done."


