@echo off
chcp 65001 >nul
title 智能考试系统 - 环境配置设置

echo ========================================
echo           智能考试系统环境配置
echo ========================================
echo.

echo 🔧 正在设置环境配置...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.9+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查env.example文件是否存在
if not exist "env.example" (
    echo ❌ 错误: 找不到 env.example 文件
    pause
    exit /b 1
)

:: 复制env.example为.env
if exist ".env" (
    echo ⚠️  .env 文件已存在
    set /p overwrite="是否覆盖现有配置？(y/N): "
    if /i not "%overwrite%"=="y" (
        echo ✅ 取消操作
        pause
        exit /b 0
    )
)

echo 📝 复制配置文件...
copy "env.example" ".env" >nul

:: 运行Python配置脚本
echo 🐍 运行配置脚本...
python setup_env.py

echo.
echo 🎉 环境配置完成！
echo.
echo 📋 下一步操作:
echo 1. 检查 .env 文件中的配置
echo 2. 启动MySQL服务
echo 3. 进入server目录: cd server
echo 4. 运行迁移: python manage.py migrate
echo 5. 创建管理员: python manage.py createsuperuser
echo 6. 启动服务: python manage.py runserver
echo.
echo 📖 详细说明请查看: 环境配置文件说明.md
echo.
pause
