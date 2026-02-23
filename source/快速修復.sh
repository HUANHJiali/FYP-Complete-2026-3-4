#!/bin/bash

echo "🔧 MySQL 連接問題快速修復腳本"
echo "========================================"
echo

# 檢查 MySQL 服務狀態
echo "🔍 檢查 MySQL 服務狀態..."
if service mysql status >/dev/null 2>&1; then
    echo "✅ MySQL 服務正在運行"
else
    echo "🔄 啟動 MySQL 服務..."
    sudo service mysql start
    sleep 3
fi

# 測試 MySQL 連接
echo "🔍 測試 MySQL 連接..."
if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ MySQL 連接正常"
    echo "🎉 可以繼續部署了！"
    echo ""
    echo "請重新運行："
    echo "./一鍵部署.sh"
else
    echo "❌ MySQL 連接失敗，需要設置密碼"
    echo ""
    echo "🔧 請執行以下步驟："
    echo "1. 設置 MySQL root 密碼："
    echo "   sudo mysql -u root"
    echo ""
    echo "2. 在 MySQL 中運行："
    echo "   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';"
    echo "   FLUSH PRIVILEGES;"
    echo "   EXIT;"
    echo ""
    echo "3. 然後重新運行："
    echo "   ./一鍵部署.sh"
fi
