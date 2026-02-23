#!/bin/bash
# SSL证书配置脚本 - 使用Let's Encrypt

set -e

echo "================================"
echo "FYP项目SSL证书配置脚本"
echo "================================"
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本"
    exit 1
fi

# 配置变量
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@example.com"}
WEBROOT="/var/www/html"

echo "域名: $DOMAIN"
echo "邮箱: $EMAIL"
echo ""

# 检查Certbot是否已安装
if ! command -v certbot &> /dev/null; then
    echo "Certbot未安装，正在安装..."

    # 检测操作系统
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        apt update
        apt install -y certbot python3-certbot-nginx
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS
        yum install -y certbot python3-certbot-nginx
    else
        echo "不支持的操作系统"
        exit 1
    fi

    echo "Certbot安装完成"
    echo ""
fi

# 创建Web根目录（如果不存在）
mkdir -p "$WEBROOT"

# 方法1: 使用standalone模式（适用于尚未配置Nginx的情况）
echo "方法1: 使用standalone模式获取SSL证书"
echo "请确保80端口未被占用"
echo ""

read -p "是否使用standalone模式？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在获取SSL证书..."

    certbot certonly --standalone \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive

    if [ $? -eq 0 ]; then
        echo "✅ SSL证书获取成功！"
        echo "证书路径: /etc/letsencrypt/live/$DOMAIN/"
    else
        echo "❌ SSL证书获取失败"
        exit 1
    fi
else
    # 方法2: 使用webroot模式（适用于已配置Nginx的情况）
    echo "方法2: 使用webroot模式获取SSL证书"
    echo "请确保Nginx已配置且Web根目录正确"
    echo ""

    read -p "是否使用webroot模式？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在获取SSL证书..."

        certbot certonly --webroot \
            -w "$WEBROOT" \
            -d "$DOMAIN" \
            -d "www.$DOMAIN" \
            --email "$EMAIL" \
            --agree-tos \
            --non-interactive

        if [ $? -eq 0 ]; then
            echo "✅ SSL证书获取成功！"
            echo "证书路径: /etc/letsencrypt/live/$DOMAIN/"
        else
            echo "❌ SSL证书获取失败"
            exit 1
        fi
    else
        echo "取消操作"
        exit 0
    fi
fi

echo ""
echo "================================"
echo "SSL证书配置完成！"
echo "================================"
echo ""
echo "证书文件位置："
echo "  证书: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  私钥: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "  链: /etc/letsencrypt/live/$DOMAIN/chain.pem"
echo ""
echo "下一步："
echo "1. 更新Nginx配置文件中的域名"
echo "2. 复制SSL配置到Nginx配置目录"
echo "3. 重启Nginx服务"
echo ""
echo "自动续期配置："
echo "Certbot已自动配置cron任务进行证书续期"
echo "可以使用 'certbot renew --dry-run' 测试续期"
echo ""

# 配置自动续期
echo "配置证书自动续期..."
(crontab -l 2>/dev/null; echo "0 0,12 * * * root certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

echo "✅ 自动续期已配置（每天0:00和12:00检查）"
echo ""

# 测试续期
echo "测试证书续期..."
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo "✅ 证书续期测试成功"
else
    echo "⚠️ 证书续期测试失败，请检查配置"
fi

echo ""
echo "配置完成！"
