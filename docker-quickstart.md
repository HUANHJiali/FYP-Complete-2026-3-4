# 🐳 Docker 快速开始

## 五分钟快速部署指南

### 1. 安装 Docker Desktop

**Windows**: [下载地址](https://www.docker.com/products/docker-desktop-windows/)  
**Mac**: [下载地址](https://www.docker.com/products/docker-desktop-mac/)  
**Linux**: [安装指南](https://docs.docker.com/engine/install/)

### 2. 启动项目

```bash
# Windows
docker-start.bat

# Mac/Linux
chmod +x docker-start.sh
./docker-start.sh
```

### 3. 等待启动

首次运行需要下载镜像，约需 3-5 分钟。  
看到 "启动成功!" 即表示部署完成。

### 4. 访问系统

- **前端**: http://localhost:8080
- **后端**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin

### 5. 登录

| 角色   | 用户名   | 密码   |
|--------|----------|--------|
| 管理员 | admin    | 123456 |
| 教师   | teacher  | 123456 |
| 学生   | student  | 123456 |

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新启动
docker-compose restart
```

## 遇到问题？

查看详细文档：[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

**就这么简单！无需安装 Python、Node.js、MySQL！**
