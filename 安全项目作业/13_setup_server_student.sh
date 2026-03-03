#!/usr/bin/env bash
set -euo pipefail

# Student-friendly single-server deployment script (Ubuntu 22.04+)
# Usage:
#   bash 13_setup_server_student.sh \
#     --repo-url <repo_url> \
#     --domain <your_domain_or_ip> \
#     --app-dir /opt/fyp

REPO_URL=""
DOMAIN=""
APP_DIR="/opt/fyp"
ENV_FILE=".env.prod"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      REPO_URL="$2"; shift 2 ;;
    --domain)
      DOMAIN="$2"; shift 2 ;;
    --app-dir)
      APP_DIR="$2"; shift 2 ;;
    *)
      echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$DOMAIN" ]]; then
  echo "Usage: bash 13_setup_server_student.sh --repo-url <repo_url> --domain <domain_or_ip> [--app-dir /opt/fyp]"
  exit 1
fi

echo "[1/8] Install dependencies..."
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release git nginx

if ! command -v docker >/dev/null 2>&1; then
  echo "[2/8] Install Docker..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  newgrp docker <<'EOF'
true
EOF
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[3/8] Install Docker Compose plugin..."
  sudo apt install -y docker-compose-plugin
fi

echo "[4/8] Clone/Update project..."
if [[ -d "$APP_DIR/.git" ]]; then
  cd "$APP_DIR"
  git pull
else
  sudo mkdir -p "$(dirname "$APP_DIR")"
  sudo chown -R "$USER":"$USER" "$(dirname "$APP_DIR")"
  git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[5/8] Create .env.prod from template..."
  if [[ -f "安全项目作业/14_env_prod_student_template.env" ]]; then
    cp "安全项目作业/14_env_prod_student_template.env" "$ENV_FILE"
  else
    cp ".env.production.example" "$ENV_FILE"
  fi
  echo "Please edit $APP_DIR/$ENV_FILE before next deployment run."
  echo "At minimum: SECRET_KEY, DB passwords, ALLOWED_HOSTS, CORS/CSRF origins, ZHIPUAI_API_KEY"
fi

echo "[6/8] Start containers..."
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" up -d --build

echo "[7/8] Configure Nginx reverse proxy..."
NGINX_CONF="/etc/nginx/sites-available/fyp_student.conf"
sudo tee "$NGINX_CONF" >/dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/fyp_student.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo "[8/8] Done. Quick checks:"
echo "- App URL: http://$DOMAIN"
echo "- Health:  http://$DOMAIN/api/health/"
echo "- Containers:"
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" ps

echo "Optional HTTPS:"
echo "sudo apt install -y certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d $DOMAIN"
