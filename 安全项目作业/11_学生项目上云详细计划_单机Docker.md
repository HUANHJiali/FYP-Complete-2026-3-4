# 学生项目上云详细计划（单机 Docker 方案）

## 1. 方案选择（推荐）
目标：低成本、快速上线、答辩稳定可演示。

推荐架构：
- 1 台 Linux 云服务器（Ubuntu 22.04）
- Docker Compose 部署：frontend + backend + mysql
- Nginx 反向代理 + HTTPS（Let’s Encrypt）

为什么适合学生：
- 与本地开发结构一致，迁移成本最低
- 问题定位简单，答辩现场更稳
- 成本可控（轻量服务器即可）

## 2. 资源规格与预算
最小可用（课程项目）：
- CPU：2 vCPU
- 内存：4 GB
- 磁盘：50 GB SSD
- 带宽：3 Mbps 及以上

推荐：
- CPU：2~4 vCPU
- 内存：4~8 GB

## 3. 云上准备清单
### 3.1 安全组/防火墙
必须开放：
- 22（SSH，仅本人 IP）
- 80（HTTP）
- 443（HTTPS）

临时调试可开放（演示后建议关闭外网直连）：
- 8080（前端容器）
- 8000（后端容器）

### 3.2 域名（可选但建议）
- 准备一个域名并解析 A 记录到云服务器公网 IP
- 用于申请 HTTPS 证书和答辩展示

## 4. 一次性初始化（服务器）
登录服务器后执行：

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release git nginx

# 安装 Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# 安装 Docker Compose 插件（若系统未自带）
sudo apt install -y docker-compose-plugin

docker --version
docker compose version
```

## 5. 代码与配置
```bash
cd /opt
sudo git clone <你的仓库地址> fyp
sudo chown -R $USER:$USER /opt/fyp
cd /opt/fyp
```

创建生产环境变量文件 `.env.prod`（示例）：
```env
MYSQL_ROOT_PASSWORD=请改成强密码
DB_NAME=db_exam
DB_USER=examuser
DB_PASSWORD=请改成强密码
DB_HOST=db
DB_PORT=3306

SECRET_KEY=请替换成高强度随机字符串
DEBUG=False
ALLOWED_HOSTS=你的域名,你的公网IP
CORS_ALLOWED_ORIGINS=https://你的域名,http://你的域名
CSRF_TRUSTED_ORIGINS=https://你的域名,http://你的域名

ZHIPUAI_API_KEY=你的key
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

## 6. 启动方式（优先用生产 compose）
```bash
cd /opt/fyp

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml ps
```

初始化检查：
```bash
docker logs fyp_backend_prod --tail 200
docker logs fyp_frontend_prod --tail 200
```

## 7. Nginx 反向代理（域名方式）
编辑 `/etc/nginx/sites-available/fyp.conf`：

```nginx
server {
    listen 80;
    server_name 你的域名;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用并重载：
```bash
sudo ln -s /etc/nginx/sites-available/fyp.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 8. HTTPS 证书（可选但强烈建议）
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名
sudo certbot renew --dry-run
```

## 9. 上线后验收（答辩前必做）
- 页面可访问：`https://你的域名`
- 健康检查：`https://你的域名/api/health/`
- 三个角色可登录（admin/teacher/student）
- 考试链路可走通：学生提交 -> 教师发布 -> 学生查看结果

建议执行项目内一键验证：
```bash
cd /opt/fyp
python feature_smoke_check_20260301.py
```

## 10. 运维与回滚
### 10.1 常用命令
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f backend
docker compose -f docker-compose.prod.yml --env-file .env.prod restart backend frontend
```

### 10.2 快速回滚
```bash
cd /opt/fyp
git log --oneline -5
git checkout <上一个稳定提交>
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 11. 7 天执行计划（学生版）
- Day 1：买服务器、装 Docker、拉代码
- Day 2：配置 `.env.prod`，容器启动
- Day 3：Nginx + 域名 + HTTPS
- Day 4：功能验收与截图留证
- Day 5：性能与稳定性复查（重启后验证）
- Day 6：演示彩排（按口播稿）
- Day 7：答辩当天只做只读检查，不改核心配置

## 12. 答辩建议
- 现场优先演示“稳定性证据”：容器健康 + 冒烟通过
- 再演示“业务闭环”：交卷、发布、查成绩
- 最后演示“安全改进点”：状态机一致性、输入校验、提交稳定性
