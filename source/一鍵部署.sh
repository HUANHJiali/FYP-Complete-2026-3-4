#!/bin/bash

# 設置錯誤處理
set -e  # 遇到錯誤立即退出
set -u  # 使用未定義變量時報錯

# 設置日誌
LOG_FILE="deployment.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================"
echo "        FYP2025 智能考试系统一键部署"
echo "========================================"
echo
echo "📝 部署日志将保存到: $LOG_FILE"
echo

echo "🚀 开始一键部署..."
echo

# 检查并安装Python
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，正在自动安装..."
    echo
    
    # 检测操作系统并安装Python
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt &> /dev/null; then
            echo "🔧 使用apt安装Python..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            echo "🔧 使用yum安装Python..."
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            echo "🔧 使用dnf安装Python..."
            sudo dnf install -y python3 python3-pip
        else
            echo "❌ 无法自动安装Python，请手动安装"
            echo "📥 Ubuntu/Debian: sudo apt install python3 python3-pip"
            echo "📥 CentOS/RHEL: sudo yum install python3 python3-pip"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "🔧 使用Homebrew安装Python..."
            brew install python3
        else
            echo "❌ 未找到Homebrew，请先安装Homebrew或手动安装Python"
            echo "📥 安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "📥 然后运行: brew install python3"
            exit 1
        fi
    else
        echo "❌ 不支持的操作系统，请手动安装Python 3.9+"
        exit 1
    fi
    echo "✅ Python安装完成"
else
    echo "✅ Python环境正常"
fi

# 检查并安装Node.js
echo "📋 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，正在自动安装..."
    echo
    
    # 检测操作系统并安装Node.js
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt &> /dev/null; then
            echo "🔧 使用apt安装Node.js..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
        elif command -v yum &> /dev/null; then
            echo "🔧 使用yum安装Node.js..."
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
        elif command -v dnf &> /dev/null; then
            echo "🔧 使用dnf安装Node.js..."
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo dnf install -y nodejs
        else
            echo "❌ 无法自动安装Node.js，请手动安装"
            echo "📥 下载地址: https://nodejs.org/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "🔧 使用Homebrew安装Node.js..."
            brew install node
        else
            echo "❌ 未找到Homebrew，请先安装Homebrew或手动安装Node.js"
            echo "📥 安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "📥 然后运行: brew install node"
            exit 1
        fi
    else
        echo "❌ 不支持的操作系统，请手动安装Node.js 16+"
        exit 1
    fi
    echo "✅ Node.js安装完成"
else
    echo "✅ Node.js环境正常"
fi

# 检查并安装MySQL
echo "📋 检查MySQL环境..."
if ! command -v mysql &> /dev/null; then
    echo "❌ 未找到MySQL，正在自动安装..."
    echo
    
    # 检测操作系统并安装MySQL
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt &> /dev/null; then
            echo "🔧 使用apt安装MySQL..."
            sudo apt update
            sudo apt install -y mysql-server
            sudo systemctl start mysql
            sudo systemctl enable mysql
        elif command -v yum &> /dev/null; then
            echo "🔧 使用yum安装MySQL..."
            sudo yum install -y mysql-server
            sudo systemctl start mysqld
            sudo systemctl enable mysqld
        elif command -v dnf &> /dev/null; then
            echo "🔧 使用dnf安装MySQL..."
            sudo dnf install -y mysql-server
            sudo systemctl start mysqld
            sudo systemctl enable mysqld
        else
            echo "❌ 无法自动安装MySQL，请手动安装"
            echo "📥 Ubuntu/Debian: sudo apt install mysql-server"
            echo "📥 CentOS/RHEL: sudo yum install mysql-server"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "🔧 使用Homebrew安装MySQL..."
            brew install mysql
            brew services start mysql
        else
            echo "❌ 未找到Homebrew，请先安装Homebrew或手动安装MySQL"
            echo "📥 安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "📥 然后运行: brew install mysql"
            exit 1
        fi
    else
        echo "❌ 不支持的操作系统，请手动安装MySQL 8.0+"
        exit 1
    fi
    echo "✅ MySQL安装完成"
    echo "⚠️  请运行 'sudo mysql_secure_installation' 来配置MySQL安全设置"
else
    echo "✅ MySQL环境正常"
fi

# 确保MySQL服务正在运行
echo "🔧 确保MySQL服务正在运行..."

# 检测是否在容器环境中
if [ -f /.dockerenv ] || [ -n "${CODESPACES:-}" ] || [ -n "${GITHUB_CODESPACE_TOKEN:-}" ]; then
    echo "🐳 检测到容器环境 (Docker/Codespaces)"
    
    # 使用 service 命令启动 MySQL
    # 首先尝试连接测试
    if mysql -u root -e "SELECT 1;" >/dev/null 2>&1 || mysql -u root -p123456 -e "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ MySQL服务正在运行"
    elif pgrep mysqld >/dev/null 2>&1; then
        echo "✅ MySQL进程正在运行"
    else
        echo "🔄 在容器环境中启动MySQL服务..."
        sudo service mysql start
        echo "⏳ 等待MySQL服务完全启动..."
        sleep 5
        
        # 再次检查服务状态 - 使用更宽松的检查
        echo "🔍 检查MySQL服务状态..."
        
        # 首先尝试直接连接测试
        if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
            echo "✅ MySQL服务启动成功（通过连接测试）"
        elif mysql -u root -p123456 -e "SELECT 1;" >/dev/null 2>&1; then
            echo "✅ MySQL服务启动成功（通过密码连接测试）"
        else
            # 检查进程是否存在
            if pgrep mysqld >/dev/null 2>&1; then
                echo "✅ MySQL进程正在运行"
            else
                echo "❌ MySQL服务启动失败，请手动检查"
                echo "🔧 尝试手动启动："
                echo "   sudo service mysql start"
                echo "   检查状态: sudo service mysql status"
                echo "   查看日志: sudo tail -f /var/log/mysql/error.log"
                echo "   设置密码: sudo mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456'; FLUSH PRIVILEGES;\""
                exit 1
            fi
        fi
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux 系统环境
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet mysql; then
            echo "✅ MySQL服务正在运行"
        elif systemctl is-active --quiet mysqld; then
            echo "✅ MySQL服务正在运行"
        else
            echo "🔄 启动MySQL服务..."
            sudo systemctl start mysql 2>/dev/null || sudo systemctl start mysqld
            sudo systemctl enable mysql 2>/dev/null || sudo systemctl enable mysqld
            echo "⏳ 等待MySQL服务完全启动..."
            sleep 5
            
            # 再次检查服务状态
            if systemctl is-active --quiet mysql || systemctl is-active --quiet mysqld; then
                echo "✅ MySQL服务启动成功"
            else
                echo "❌ MySQL服务启动失败，请手动检查"
                echo "🔧 尝试手动启动："
                echo "   sudo systemctl start mysql"
                echo "   或: sudo systemctl start mysqld"
                echo "   然后检查状态: sudo systemctl status mysql"
                exit 1
            fi
        fi
    else
        # 使用 service 命令
        if service mysql status >/dev/null 2>&1; then
            echo "✅ MySQL服务正在运行"
        else
            echo "🔄 启动MySQL服务..."
            sudo service mysql start
            echo "⏳ 等待MySQL服务完全启动..."
            sleep 5
            
            if service mysql status >/dev/null 2>&1; then
                echo "✅ MySQL服务启动成功"
            else
                echo "❌ MySQL服务启动失败，请手动检查"
                echo "🔧 尝试手动启动："
                echo "   sudo service mysql start"
                exit 1
            fi
        fi
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        if brew services list | grep mysql | grep started >/dev/null; then
            echo "✅ MySQL服务正在运行"
        else
            echo "🔄 启动MySQL服务..."
            brew services start mysql
            echo "⏳ 等待MySQL服务完全启动..."
            sleep 5
            
            # 再次检查服务状态
            if brew services list | grep mysql | grep started >/dev/null; then
                echo "✅ MySQL服务启动成功"
            else
                echo "❌ MySQL服务启动失败，请手动检查"
                echo "🔧 尝试手动启动："
                echo "   brew services start mysql"
                echo "   然后检查状态: brew services list | grep mysql"
                exit 1
            fi
        fi
    fi
fi

# 运行环境配置
echo
echo "🔧 配置环境..."
chmod +x setup_env.sh
./setup_env.sh
if [ $? -ne 0 ]; then
    echo "❌ 环境配置失败"
    exit 1
fi

# 设置数据库
echo
echo "🗄️ 设置数据库..."

# 读取一次 MySQL root 密码并重用
echo "读取一次 MySQL root 密码并重用"
read -s -p "MySQL root 密码: " MYSQL_PWD
echo

# 测试MySQL连接
echo "🔍 测试MySQL连接..."
if ! mysql -u root -p"$MYSQL_PWD" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "❌ MySQL连接失败，请检查："
    echo "   1. MySQL服务是否启动"
    echo "   2. root密码是否正确"
    echo "   3. 是否有连接权限"
    echo ""
    echo "🔧 尝试启动MySQL服务："
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   sudo systemctl start mysql"
        echo "   或: sudo systemctl start mysqld"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew services start mysql"
    fi
    echo ""
    echo "🔧 如果MySQL未设置密码，请运行："
    echo "   sudo mysql_secure_installation"
    echo ""
    read -p "按回车键继续（请先解决MySQL连接问题）..."
    exit 1
fi

echo "创建数据库..."
if ! mysql -u root -p"$MYSQL_PWD" -e "CREATE DATABASE IF NOT EXISTS db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"; then
    echo "⚠️ 数据库创建失败，请检查MySQL服务、root密码或权限"
fi

# 导入数据库
echo "导入数据库结构..."
if [ -f "../database/db_exam.sql" ]; then
    if ! mysql -u root -p"$MYSQL_PWD" db_exam < ../database/db_exam.sql; then
        echo "⚠️ 数据库结构导入失败，请检查SQL文件或权限"
    fi
else
    echo "❌ 未找到 ../database/db_exam.sql"
fi

echo "导入初始数据..."
if [ -f "../database/init_practice_data.sql" ]; then
    if ! mysql -u root -p"$MYSQL_PWD" db_exam < ../database/init_practice_data.sql; then
        echo "⚠️ 初始数据导入失败，请检查SQL文件或权限"
    fi
else
    echo "❌ 未找到 ../database/init_practice_data.sql"
fi

# 设置后端
echo
echo "🐍 设置后端环境..."
if [ ! -d "server" ]; then
    echo "❌ 未找到server目录，请确保在正确的项目目录中运行脚本"
    exit 1
fi
cd server

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "❌ 虚拟环境创建失败"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Python依赖安装失败"
    exit 1
fi

# 运行迁移
echo "运行数据库迁移..."
python3 manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 创建管理员
echo "创建管理员账户..."
python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin','admin@example.com','123456') if not User.objects.filter(username='admin').exists() else print('管理员已存在')"

# 启动后端服务
echo
echo "🚀 启动后端服务..."
echo "后端服务将在 http://localhost:8000 启动"
echo "请保持此终端打开，然后打开新的终端窗口继续前端设置"
echo
echo "按任意键启动后端服务..."
read -p "按回车键继续..."

# 在新终端启动后端
echo "🔄 尝试在新终端启动后端服务..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd $(pwd) && source .venv/bin/activate && python3 manage.py runserver; exec bash" &
    echo "✅ 后端服务已在新终端启动"
elif command -v xterm &> /dev/null; then
    xterm -e "cd $(pwd) && source .venv/bin/activate && python3 manage.py runserver" &
    echo "✅ 后端服务已在新终端启动"
elif command -v konsole &> /dev/null; then
    konsole --new-tab -e bash -c "cd $(pwd) && source .venv/bin/activate && python3 manage.py runserver" &
    echo "✅ 后端服务已在新终端启动"
else
    echo "⚠️  无法自动启动新终端，请手动操作："
    echo "   1. 打开新终端窗口"
    echo "   2. 运行: cd $(pwd)"
    echo "   3. 运行: source .venv/bin/activate"
    echo "   4. 运行: python3 manage.py runserver"
    echo ""
    echo "按回车键继续前端设置..."
    read -p "按回车键继续..."
fi

# 设置前端
echo
echo "🎨 设置前端环境..."
if [ ! -d "../client" ]; then
    echo "❌ 未找到client目录，请确保在正确的项目目录中运行脚本"
    exit 1
fi
cd ../client

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 未找到package.json文件"
    exit 1
fi

# 安装依赖
echo "安装Node.js依赖..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Node.js依赖安装失败"
    exit 1
fi

# 启动前端服务
echo
echo "🚀 启动前端服务..."
echo "前端服务将在 http://localhost:8080 启动"
echo
echo "按任意键启动前端服务..."
read -p "按回车键继续..."

# 在新终端启动前端
echo "🔄 尝试在新终端启动前端服务..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd $(pwd) && npm run serve; exec bash" &
    echo "✅ 前端服务已在新终端启动"
elif command -v xterm &> /dev/null; then
    xterm -e "cd $(pwd) && npm run serve" &
    echo "✅ 前端服务已在新终端启动"
elif command -v konsole &> /dev/null; then
    konsole --new-tab -e bash -c "cd $(pwd) && npm run serve" &
    echo "✅ 前端服务已在新终端启动"
else
    echo "⚠️  无法自动启动新终端，请手动操作："
    echo "   1. 打开新终端窗口"
    echo "   2. 运行: cd $(pwd)"
    echo "   3. 运行: npm run serve"
    echo ""
    echo "按回车键完成部署..."
    read -p "按回车键完成..."
fi

echo
echo "========================================"
echo "           部署完成！"
echo "========================================"
echo
echo "🌐 访问地址:"
echo "  前端界面: http://localhost:8080"
echo "  后端API:  http://localhost:8000"
echo "  管理后台: http://localhost:8000/admin"
echo
echo "👤 测试账户:"
echo "  管理员: admin / 123456"
echo "  教师:   teacher / 123456"
echo "  学生:   student / 123456"
echo
echo "🎉 系统部署成功！请访问 http://localhost:8080 开始使用"
echo
