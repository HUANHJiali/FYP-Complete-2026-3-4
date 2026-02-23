#!/bin/bash

echo "========================================"
echo "           智能考试系统环境配置"
echo "========================================"
echo

echo "🔧 正在设置环境配置..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.9+"
    echo "📥 Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "📥 CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "📥 macOS: brew install python3"
    exit 1
fi

# 检查Python版本
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: Python版本过低，需要Python 3.9+，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查env.example文件是否存在
if [ ! -f "env.example" ]; then
    echo "❌ 错误: 找不到 env.example 文件"
    exit 1
fi

# 复制env.example为.env
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在"
    read -p "是否覆盖现有配置？(y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "✅ 取消操作"
        exit 0
    fi
fi

echo "📝 复制配置文件..."
cp "env.example" ".env"

# 运行Python配置脚本
echo "🐍 运行配置脚本..."
python3 setup_env.py

echo
echo "🎉 环境配置完成！"
echo
echo "📋 下一步操作:"
echo "1. 检查 .env 文件中的配置"
echo "2. 启动MySQL服务: sudo service mysql start"
echo "3. 进入server目录: cd server"
echo "4. 创建虚拟环境: python3 -m venv .venv"
echo "5. 激活虚拟环境: source .venv/bin/activate"
echo "6. 安装依赖: pip install -r requirements.txt"
echo "7. 运行迁移: python manage.py migrate"
echo "8. 创建管理员: python manage.py createsuperuser"
echo "9. 启动服务: python manage.py runserver"
echo
echo "📖 详细说明请查看: 环境配置文件说明.md"
echo
