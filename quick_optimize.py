"""
FYP项目快速优化工具 - 可立即执行的优化
"""
import os

def apply_optimization_1_cache():
    """优化1: 配置缓存系统"""
    settings_path = 'source/server/server/settings.py'

    print("Applying Optimization 1: Cache Configuration...")

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查CACHES是否已配置
    if 'CACHES = {' in content:
        print("[-] CACHES already configured, skipping...")
        return False

    # 找到INSTALLED_APPS的位置
    installed_apps_pos = content.find('INSTALLED_APPS = [')
    if installed_apps_pos == -1:
        print("[-] Cannot find INSTALLED_APPS")
        return False

    # 在INSTALLED_APPS后面插入CACHES配置
    cache_config = """

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
"""

    # 在INSTALLED_APPS块结束后插入
    insert_pos = content.find('\n]', installed_apps_pos)
    if insert_pos != -1:
        insert_pos += 2  # 跳过'\n]'
        content = content[:insert_pos] + cache_config + content[insert_pos:]

        # 备份原文件
        os.system('copy source\\server\\server\\settings.py source\\server\\server\\settings.py.backup')

        # 写入新内容
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("[+] Cache configuration added")
        return True
    else:
        print("[-] Cannot find insertion point")
        return False


def apply_optimization_2_middleware():
    """优化2: 启用性能监控中间件"""
    settings_path = 'source/server/server/settings.py'

    print("Applying Optimization 2: Performance Monitoring...")

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已启用
    if 'PerformanceMonitorMiddleware' in content:
        print("[-] PerformanceMonitorMiddleware already enabled, skipping...")
        return False

    # 找到MIDDLEWARE列表
    middleware_start = content.find('MIDDLEWARE = [')
    if middleware_start == -1:
        print("[-] Cannot find MIDDLEWARE")
        return False

    # 找到MIDDLEWARE列表的第一个元素
    first_element_pos = content.find("'", middleware_start)
    if first_element_pos == -1:
        first_element_pos = content.find('"', middleware_start)

    # 在第一个元素前插入
    if first_element_pos != -1:
        indent = '    '
        new_middleware = f"{indent}'comm.performance_monitor.PerformanceMonitorMiddleware',\n"
        content = content[:first_element_pos + 1] + new_middleware + content[first_element_pos + 1:]

        # 备份
        os.system('copy source\\server\\server\\settings.py source\\server\\server\\settings.py.backup2')

        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("[+] Performance monitoring middleware enabled")
        return True
    else:
        print("[-] Cannot parse MIDDLEWARE list")
        return False


def apply_optimization_3_ratelimit():
    """优化3: 启用API限流"""
    settings_path = 'source/server/server/settings.py'

    print("Applying Optimization 3: Rate Limiting...")

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查django-ratelimit是否在INSTALLED_APPS中
    if "'django-ratelimit'" in content or '"django-ratelimit"' in content:
        # 检查是否启用
        if "'django-ratelimit'," in content or '"django-ratelimit",' in content:
            print("[+] Rate limiting already enabled")
            return True
        else:
            # 需要添加到INSTALLED_APPS
            installed_apps_pos = content.find('INSTALLED_APPS = [')
            if installed_apps_pos == -1:
                print("[-] Cannot find INSTALLED_APPS")
                return False

            # 在app后面添加
            app_pos = content.find("'app',", installed_apps_pos)
            if app_pos == -1:
                print("[-] Cannot find 'app' in INSTALLED_APPS")
                return False

            # 在app后插入
            insert_pos = content.find(',', app_pos)
            if insert_pos != -1:
                content = content[:insert_pos] + "\n    'django-ratelimit'," + content[insert_pos:]

                os.system('copy source\\server\\server\\settings.py source\\server\\server\\settings.py.backup3')

                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print("[+] django-ratelimit added to INSTALLED_APPS")
                return True
    else:
        print("[-] django-ratelimit not installed")
        print("[!] Install with: pip install django-ratelimit")
        return False


def apply_optimization_4_health_check():
    """优化4: 增强健康检查"""
    health_check_path = 'source/health_check.py'

    print("Applying Optimization 4: Enhanced Health Check...")

    # 检查文件是否存在
    if not os.path.exists(health_check_path):
        print("[-] health_check.py not found")
        return False

    with open(health_check_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否需要增强
    if 'database' in content.lower() and 'cache' in content.lower():
        print("[-] Health check already enhanced")
        return False

    # 增强健康检查
    enhanced_health_check = '''
def health_check(request):
    """Enhanced health check with system status"""
    import os
    import sys
    from datetime import datetime

    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('DJANGO_SETTINGS_MODULE', 'unknown'),
        'python_version': sys.version,
        'components': {}
    }

    # Check database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status['components']['database'] = 'healthy'
    except Exception as e:
        status['components']['database'] = f'unhealthy: {str(e)[:50]}'
        status['status'] = 'degraded'

    # Check cache
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['components']['cache'] = 'healthy'
    except Exception as e:
        status['components']['cache'] = f'unhealthy: {str(e)[:50]}'
        status['status'] = 'degraded'

    from django.http import JsonResponse
    return JsonResponse(status)
'''

    # 备份
    os.system('copy source\\health_check.py source\\health_check.py.backup')

    with open(health_check_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_health_check)

    print("[+] Enhanced health check implemented")
    return True


def create_backup_script():
    """创建数据库备份脚本"""
    script_content = '''#!/bin/bash
# Database Backup Script
# Run this to backup the database

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
MYSQL_CONTAINER="fyp_mysql"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
DATABASE="db_exam"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting database backup..."
echo "Date: $DATE"

# Backup database
docker exec $MYSQL_CONTAINER mysqldump -u$MYSQL_USER -p$MYSQL_PASSWORD $DATABASE > $BACKUP_DIR/db_exam_$DATE.sql

if [ $? -eq 0 ]; then
    echo "Backup completed successfully!"
    echo "Backup file: $BACKUP_DIR/db_exam_$DATE.sql"
    echo "Size: $(du -h $BACKUP_DIR/db_exam_$DATE.sql | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi
'''

    with open('backup_database.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)

    # 添加执行权限
    os.system('chmod +x backup_database.sh')

    print("[+] Database backup script created: backup_database.sh")
    return True


def create_log_rotation_config():
    """创建日志轮转配置"""
    config_content = '''# Log Rotation Configuration for FYP Project
# Place this in /etc/logrotate.d/fyp-project

/var/log/exam/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn >/dev/null 2>&1 || true
    endscript
}
'''

    with open('logrotate.conf', 'w', encoding='utf-8') as f:
        f.write(config_content)

    print("[+] Log rotation configuration created: logrotate.conf")
    print("[!] Install with: sudo cp logrotate.conf /etc/logrotate.d/")
    return True


def create_deployment_guide():
    """创建部署指南"""
    guide_content = '''# FYP Project Deployment Guide

## Production Deployment

### Prerequisites
- Ubuntu 20.04+ server
- Docker and Docker Compose
- Python 3.9+
- Node.js 16+

### Quick Start

1. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd FYP2025-12-27-main
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit configuration
   ```

3. **Start Services**
   ```bash
   sudo docker-compose up -d
   ```

4. **Run Migrations**
   ```bash
   sudo docker-compose exec backend python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   sudo docker-compose exec backend python manage.py createsuperuser
   ```

### Nginx Configuration (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/HTTPS Configuration

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL Certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Backup Strategy

1. **Database Backup** (Daily)
   ```bash
   ./backup_database.sh
   ```

2. **Media Files Backup** (Weekly)
   ```bash
   tar -czf backups/media_$(date +%Y%m%d).tar.gz source/server/media/
   ```

3. **Code Backup** (Before each deployment)
   ```bash
   git add .
   git commit -m "Pre-deployment backup"
   ```

### Monitoring

1. **Check Service Status**
   ```bash
   sudo docker-compose ps
   sudo docker-compose logs backend
   ```

2. **Check Disk Space**
   ```bash
   df -h
   ```

3. **Check Memory Usage**
   ```bash
   free -h
   ```

### Troubleshooting

**Service won't start**
```bash
sudo docker-compose logs backend
sudo docker-compose logs frontend
```

**Database connection error**
```bash
sudo docker-compose logs db
sudo docker-compose exec db mysql -uroot -p123456 -e "SHOW PROCESSLIST;"
```

**High CPU usage**
```bash
sudo docker stats
```

### Rollback Procedure

If deployment fails:

1. ```bash
   sudo docker-compose down
   git log --oneline -5  # See last 5 commits
   git checkout <previous-commit>
   sudo docker-compose up -d --build
   ```

2. Restore database backup:
   ```bash
   sudo docker-compose exec -T db mysql -uroot -p123456 db_exam < backups/db_exam_YYYYMMDD.sql
   ```

---

## Maintenance

### Regular Tasks

**Daily:**
- Check service status
- Monitor disk space
- Review error logs

**Weekly:**
- Database backup
- Review access logs
- Security updates

**Monthly:**
- Update dependencies
- Review and optimize database
- Test backup restoration
- Security audit

### Update Procedure

1. Test in staging environment
2. Backup database
3. Create git branch
4. Apply updates
5. Test thoroughly
6. Deploy to production
7. Monitor for issues
8. Rollback if needed

---

## Emergency Procedures

### Database Corruption

1. Stop services
2. Restore from backup
3. Run integrity check
4. Restart services

### Security Breach

1. Isolate affected systems
2. Change all passwords
3. Review access logs
4. Patch vulnerabilities
5. Notify stakeholders

### DDoS Attack

1. Enable rate limiting
2. Configure firewall
3. Use DDoS protection service
4. Enable cloudflare

---

## Contact

For issues or questions:
- GitHub Issues
- Email: admin@example.com
'''

    with open('DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)

    print("[+] Deployment guide created: DEPLOYMENT_GUIDE.md")
    return True


def main():
    """执行快速优化"""
    print("="*70)
    print("  FYP Project Quick Optimizer")
    print("="*70)
    print()
    print("This will apply quick optimizations to your project.")
    print()

    optimizations = [
        ("Configure Cache System", apply_optimization_1_cache),
        ("Enable Performance Monitoring", apply_optimization_2_middleware),
        ("Enable Rate Limiting", apply_optimization_3_ratelimit),
        ("Enhance Health Check", apply_optimization_4_health_check),
        ("Create Backup Script", create_backup_script),
        ("Create Log Rotation", create_log_rotation_config),
        ("Create Deployment Guide", create_deployment_guide),
    ]

    print("Available Optimizations:")
    for i, (name, func) in enumerate(optimizations, 1):
        print(f"{i}. {name}")

    print()
    print("I will execute all optimizations.")
    print()
    print("Starting...")
    print()

    results = []
    for name, func in optimizations:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)[:50]}")
            results.append((name, False))

    print()
    print("="*70)
    print("  Optimization Results")
    print("="*70)

    for name, result in results:
        if result:
            print(f"[OK] {name}")
        else:
            print(f"[SKIP] {name}")

    print()
    print("="*70)
    print("Next Steps:")
    print("1. Restart services: docker-compose restart")
    print("2. Verify: docker-compose logs backend")
    print("3. Test: python run_tests.py")
    print("="*70)


if __name__ == '__main__':
    main()
