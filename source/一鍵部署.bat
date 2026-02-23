@echo off
chcp 65001 >nul
title FYP2025 智能考试系统 - 一键部署

echo ========================================
echo        FYP2025 智能考试系统一键部署
echo ========================================
echo.

echo 🚀 开始一键部署...
echo.

:: 检查并安装Python（优先 winget）
echo 📋 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，优先使用 winget 安装...
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ 未检测到 winget，回退到官方安装包下载
        echo 🔧 正在下载Python安装包...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python-installer.exe'}"
        if exist python-installer.exe (
            echo 📦 正在安装Python...
            python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
            del python-installer.exe
            echo ✅ Python安装完成
        ) else (
            echo ❌ Python下载失败，请手动安装
            echo 📥 下载地址: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else (
        echo 🔧 使用 winget 安装 Python...
        winget install -e --id Python.Python.3 --silent
        if errorlevel 1 (
            echo ⚠️ winget 安装失败，回退到官方安装包
            powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python-installer.exe'}"
            if exist python-installer.exe (
                python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
                del python-installer.exe
            ) else (
                echo ❌ Python下载失败，请手动安装
                pause
                exit /b 1
            )
        )
        echo ✅ Python安装完成
    )
) else (
    echo ✅ Python环境正常
)

:: 检查并安装Node.js（优先 winget）
echo 📋 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，优先使用 winget 安装...
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ 未检测到 winget，回退到官方安装包下载
        echo 🔧 正在下载Node.js安装包...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.17.0/node-v18.17.0-x64.msi' -OutFile 'nodejs-installer.msi'}"
        if exist nodejs-installer.msi (
            echo 📦 正在安装Node.js...
            msiexec /i nodejs-installer.msi /quiet
            del nodejs-installer.msi
            echo ✅ Node.js安装完成
            echo 🔄 请重新运行此脚本以继续...
            pause
            exit /b 0
        ) else (
            echo ❌ Node.js下载失败，请手动安装
            echo 📥 下载地址: https://nodejs.org/
            pause
            exit /b 1
        )
    ) else (
        echo 🔧 使用 winget 安装 Node.js LTS...
        winget install -e --id OpenJS.NodeJS.LTS --silent
        if errorlevel 1 (
            echo ⚠️ winget 安装失败，回退到官方安装包
            powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.17.0/node-v18.17.0-x64.msi' -OutFile 'nodejs-installer.msi'}"
            if exist nodejs-installer.msi (
                msiexec /i nodejs-installer.msi /quiet
                del nodejs-installer.msi
                echo 🔄 请重新运行此脚本以继续...
                pause
                exit /b 0
            ) else (
                echo ❌ Node.js下载失败，请手动安装
                pause
                exit /b 1
            )
        )
        echo ✅ Node.js安装完成
        echo 🔄 请重新运行此脚本以继续...
        pause
        exit /b 0
    )
) else (
    echo ✅ Node.js环境正常
)

:: 检查并安装MySQL（优先 winget）
echo 📋 检查MySQL环境...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到MySQL，优先使用 winget 安装...
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ 未检测到 winget，回退到官方安装器
        echo 🔧 正在下载MySQL安装器...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.34.0.msi' -OutFile 'mysql-installer.msi'}"
        if exist mysql-installer.msi (
            echo 📦 正在安装MySQL（需要手动完成安装向导）...
            start mysql-installer.msi
            echo.
            echo 🔄 请完成MySQL安装后重新运行此脚本...
            pause
            exit /b 0
        ) else (
            echo ❌ MySQL下载失败，请手动安装: https://dev.mysql.com/downloads/mysql/
            pause
            exit /b 1
        )
    ) else (
        echo 🔧 使用 winget 安装 MySQL...
        winget install -e --id Oracle.MySQL --silent
        if errorlevel 1 (
            echo ⚠️ winget 安装失败，回退到官方安装器
            powershell -Command "& {Invoke-WebRequest -Uri 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.34.0.msi' -OutFile 'mysql-installer.msi'}"
            if exist mysql-installer.msi (
                start mysql-installer.msi
                echo 🔄 请完成MySQL安装后重新运行此脚本...
                pause
                exit /b 0
            ) else (
                echo ❌ MySQL下载失败，请手动安装
                pause
                exit /b 1
            )
        )
        echo ✅ MySQL安装完成（如需，請啟動服務）
    )
) else (
    echo ✅ MySQL环境正常
)

:: 运行环境配置
echo.
echo 🔧 配置环境...
call setup_env.bat
if errorlevel 1 (
    echo ❌ 环境配置失败
    pause
    exit /b 1
)

:: 设置数据库
echo.
echo 🗄️ 设置数据库...

:: 检查MySQL服务状态
echo 🔍 检查MySQL服务状态...
sc query mysql >nul 2>&1
if errorlevel 1 (
    echo ❌ MySQL服务未找到，请确保MySQL已正确安装
    echo 📥 下载地址: https://dev.mysql.com/downloads/mysql/
    pause
    exit /b 1
) else (
    sc query mysql | find "RUNNING" >nul
    if errorlevel 1 (
        echo 🔄 MySQL服务未运行，正在启动...
        net start mysql
        if errorlevel 1 (
            echo ❌ MySQL服务启动失败，请手动启动
            echo 🔧 请运行: net start mysql
            echo 🔧 检查服务状态: sc query mysql
            pause
            exit /b 1
        ) else (
            echo ⏳ 等待MySQL服务完全启动...
            timeout /t 5 /nobreak >nul
            echo ✅ MySQL服务启动成功
        )
    ) else (
        echo ✅ MySQL服务正在运行
    )
)

echo 请确保MySQL服务正在运行，然后按任意键继续...
pause

:: 读取一次 MySQL root 密码并重用
setlocal ENABLEDELAYEDEXPANSION
set /p MYSQL_PWD=请输入 MySQL root 密码（输入不回显，直接输入后回车）:
echo.

:: 创建数据库
echo 创建数据库...
mysql -u root -p%MYSQL_PWD% -e "CREATE DATABASE IF NOT EXISTS db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if errorlevel 1 (
    echo ⚠️ 数据库创建失败，请检查MySQL服务、root密码或权限
)

:: 导入数据库
echo 导入数据库结构...
if exist "..\database\db_exam.sql" (
    mysql -u root -p%MYSQL_PWD% db_exam < ..\database\db_exam.sql
    if errorlevel 1 (
        echo ⚠️ 数据库结构导入失败，请检查SQL文件或权限
    )
) else (
    echo ❌ 未找到 ..\database\db_exam.sql
)

echo 导入初始数据...
if exist "..\database\init_practice_data.sql" (
    mysql -u root -p%MYSQL_PWD% db_exam < ..\database\init_practice_data.sql
    if errorlevel 1 (
        echo ⚠️ 初始数据导入失败，请检查SQL文件或权限
    )
) else (
    echo ❌ 未找到 ..\database\init_practice_data.sql
)
endlocal

:: 设置后端
echo.
echo 🐍 设置后端环境...
cd server

:: 创建虚拟环境
python -m venv .venv
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

:: 激活虚拟环境
call .venv\Scripts\activate

:: 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)

:: 运行迁移
echo 运行数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)

:: 创建管理员
echo 创建管理员账户...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin','admin@example.com','123456') if not User.objects.filter(username='admin').exists() else print('管理员已存在') | python manage.py shell

:: 启动后端服务
echo.
echo 🚀 启动后端服务...
echo 后端服务将在 http://localhost:8000 启动
echo 请保持此窗口打开，然后打开新的命令行窗口继续前端设置
echo.
echo 按任意键启动后端服务...
pause

start "Django Backend" cmd /k "cd /d %~dp0server && .venv\Scripts\activate && python manage.py runserver"

:: 设置前端
echo.
echo 🎨 设置前端环境...
cd ..\client

:: 安装依赖
echo 安装Node.js依赖...
npm install
if errorlevel 1 (
    echo ❌ Node.js依赖安装失败
    pause
    exit /b 1
)

:: 启动前端服务
echo.
echo 🚀 启动前端服务...
echo 前端服务将在 http://localhost:8080 启动
echo.
echo 按任意键启动前端服务...
pause

start "Vue Frontend" cmd /k "cd /d %~dp0client && npm run serve"

echo.
echo ========================================
echo           部署完成！
echo ========================================
echo.
echo 🌐 访问地址:
echo   前端界面: http://localhost:8080
echo   后端API:  http://localhost:8000
echo   管理后台: http://localhost:8000/admin
echo.
echo 👤 测试账户:
echo   管理员: admin / 123456
echo   教师:   teacher / 123456
echo   学生:   student / 123456
echo.
echo 🎉 系统部署成功！请访问 http://localhost:8080 开始使用
echo.
pause
