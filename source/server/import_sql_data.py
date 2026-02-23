#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入SQL数据脚本
"""

import os
import sys
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

def import_sql_data():
    """导入SQL数据"""
    print("=== 开始导入SQL数据 ===")
    
    # SQL文件路径
    sql_file_path = "../数据库/db_exam.sql"
    
    if not os.path.exists(sql_file_path):
        print(f"❌ SQL文件不存在: {sql_file_path}")
        return False
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        sql_statements = sql_content.split(';')
        
        cursor = connection.cursor()
        
        # 执行每个SQL语句
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if statement and not statement.startswith('/*') and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    if i % 10 == 0:
                        print(f"已执行 {i} 个SQL语句...")
                except Exception as e:
                    # 忽略一些常见的错误（如表已存在等）
                    if "already exists" not in str(e) and "Duplicate entry" not in str(e):
                        print(f"警告: 执行SQL语句时出错: {e}")
        
        print("✅ SQL数据导入完成")
        return True
        
    except Exception as e:
        print(f"❌ 导入SQL数据失败: {e}")
        return False

if __name__ == "__main__":
    success = import_sql_data()
    if success:
        print("\n🎉 SQL数据导入成功！")
    else:
        print("\n💥 SQL数据导入失败！")

