# FYP Project Deployment Guide

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
