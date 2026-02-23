#!/bin/bash

echo "========================================"
echo "    FYP2025 容器環境專用部署腳本"
echo "========================================"
echo

echo "🐳 檢測到容器環境，使用專用部署流程..."
echo

# 檢查 MySQL 服務
echo "🔍 檢查 MySQL 服務狀態..."
if service mysql status >/dev/null 2>&1; then
    echo "✅ MySQL 服務正在運行"
else
    echo "🔄 啟動 MySQL 服務..."
    sudo service mysql start
    sleep 3
    
    if service mysql status >/dev/null 2>&1; then
        echo "✅ MySQL 服務啟動成功"
    else
        echo "❌ MySQL 服務啟動失敗"
        echo "🔧 請手動執行："
        echo "   sudo service mysql start"
        echo "   sudo service mysql status"
        exit 1
    fi
fi

# 檢查 MySQL 連接
echo "🔍 測試 MySQL 連接..."
if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ MySQL 連接正常"
else
    echo "❌ MySQL 連接失敗，請設置 root 密碼"
    echo "🔧 請執行："
    echo "   sudo mysql_secure_installation"
    echo "   或："
    echo "   sudo mysql -u root"
    echo "   然後運行："
    echo "   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';"
    echo "   FLUSH PRIVILEGES;"
    exit 1
fi

# 設置數據庫
echo "🗄️ 設置數據庫..."
read -s -p "MySQL root 密碼: " MYSQL_PWD
echo

# 創建數據庫
echo "創建數據庫..."
mysql -u root -p"$MYSQL_PWD" -e "CREATE DATABASE IF NOT EXISTS db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 導入數據庫
if [ -f "../database/db_exam.sql" ]; then
    echo "導入數據庫結構..."
    mysql -u root -p"$MYSQL_PWD" db_exam < ../database/db_exam.sql
fi

if [ -f "../database/init_practice_data.sql" ]; then
    echo "導入初始數據..."
    mysql -u root -p"$MYSQL_PWD" db_exam < ../database/init_practice_data.sql
fi

# 設置後端
echo "🐍 設置後端環境..."
cd server

# 創建虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 運行遷移
python3 manage.py migrate

# 創建管理員
python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin','admin@example.com','123456') if not User.objects.filter(username='admin').exists() else print('管理員已存在')"

# 啟動後端
echo "🚀 啟動後端服務..."
python3 manage.py runserver 0.0.0.0:8000 &

# 設置前端
echo "🎨 設置前端環境..."
cd ../client

# 安裝依賴
npm install

# 啟動前端
echo "🚀 啟動前端服務..."
npm run serve -- --host 0.0.0.0 --port 8080 &

echo
echo "========================================"
echo "           部署完成！"
echo "========================================"
echo
echo "🌐 訪問地址:"
echo "  前端界面: http://localhost:8080"
echo "  後端API:  http://localhost:8000"
echo "  管理後台: http://localhost:8000/admin"
echo
echo "👤 測試賬戶:"
echo "  管理員: admin / 123456"
echo "  教師:   teacher / 123456"
echo "  學生:   student / 123456"
echo
echo "🎉 系統部署成功！"
echo
