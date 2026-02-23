#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置快速设置脚本
Environment Configuration Quick Setup Script
"""
import os
import sys
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """生成Django SECRET_KEY"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for _ in range(50))

def create_env_file():
    """创建.env配置文件"""
    env_example_path = Path('env.example')
    env_path = Path('.env')
    
    if not env_example_path.exists():
        print("❌ 错误: 找不到 env.example 文件")
        return False
    
    if env_path.exists():
        response = input("⚠️  .env 文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("✅ 取消操作")
            return False
    
    # 读取模板文件
    with open(env_example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的SECRET_KEY
    new_secret_key = generate_secret_key()
    content = content.replace('your-secret-key-here', new_secret_key)
    
    # 写入.env文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已创建 .env 配置文件")
    print(f"🔑 已生成新的 SECRET_KEY: {new_secret_key[:20]}...")
    return True

def get_user_input():
    """获取用户输入配置"""
    config = {}
    
    print("\n📝 请输入以下配置信息 (直接回车使用默认值):")
    
    # 数据库配置
    print("\n🗄️  数据库配置:")
    config['DB_PASSWORD'] = input("数据库密码 (默认: 123456): ").strip() or "123456"
    config['DB_HOST'] = input("数据库主机 (默认: localhost): ").strip() or "localhost"
    config['DB_PORT'] = input("数据库端口 (默认: 3306): ").strip() or "3306"
    
    # AI配置
    print("\n🤖 AI服务配置 (可选):")
    config['ZHIPUAI_API_KEY'] = input("智谱AI API密钥 (可选): ").strip()
    
    # 邮件配置
    print("\n📧 邮件配置 (可选):")
    config['EMAIL_HOST_USER'] = input("邮箱地址 (可选): ").strip()
    config['EMAIL_HOST_PASSWORD'] = input("邮箱密码 (可选): ").strip()
    
    return config

def update_env_file(config):
    """更新.env文件中的配置"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ 错误: .env 文件不存在")
        return False
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新配置
    for key, value in config.items():
        if value:  # 只更新非空值
            # 查找并替换配置项
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f'{key}='):
                    lines[i] = f'{key}={value}'
                    break
            content = '\n'.join(lines)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已更新 .env 配置文件")
    return True

def check_dependencies():
    """检查依赖是否安装"""
    print("\n🔍 检查依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("❌ Python版本过低，需要Python 3.9+")
        return False
    else:
        print(f"✅ Python版本: {sys.version}")
    
    # 检查MySQL
    try:
        import pymysql
        print("✅ PyMySQL已安装")
    except ImportError:
        print("❌ PyMySQL未安装，请运行: pip install pymysql")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 智能考试系统 - 环境配置设置")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装必要的依赖")
        return
    
    # 创建.env文件
    if not create_env_file():
        return
    
    # 获取用户配置
    config = get_user_input()
    
    # 更新配置文件
    if config:
        update_env_file(config)
    
    print("\n🎉 环境配置完成！")
    print("\n📋 下一步操作:")
    print("1. 检查 .env 文件中的配置是否正确")
    print("2. 启动MySQL服务")
    print("3. 运行数据库迁移: python manage.py migrate")
    print("4. 创建管理员账户: python manage.py createsuperuser")
    print("5. 启动开发服务器: python manage.py runserver")
    
    print("\n📖 详细说明请查看: 环境配置文件说明.md")

if __name__ == "__main__":
    main()
