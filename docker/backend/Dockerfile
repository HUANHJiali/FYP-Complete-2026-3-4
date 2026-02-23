# 后端 Dockerfile - Django 服务器
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括Pillow所需的图像处理库）
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements 文件（优化 Docker 缓存）
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 设置权限
RUN chmod +x manage.py

# 默认命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
