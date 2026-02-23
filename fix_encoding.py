#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import os

# 数据库连接配置
db_config = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 3307)),
    'user': 'root',
    'password': '123456',
    'database': 'db_exam',
    'charset': 'utf8mb4'
}

try:
    # 连接数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 修复练习试卷标题
    cursor.execute("""
        UPDATE fater_practice_papers
        SET title = %s, description = %s
        WHERE id = 1
    """, ('Python基础练习', 'Python基础知识练习试卷'))

    # 修复任务标题
    cursor.execute("""
        UPDATE fater_tasks
        SET title = %s, description = %s
        WHERE id = 1
    """, ('Python函数练习', '完成Python函数练习任务'))

    # 修复系统管理员消息
    cursor.execute("""
        UPDATE fater_users
        SET name = %s
        WHERE type = 0
    """, ('系统管理员',))

    conn.commit()

    # 验证修复结果
    cursor.execute("SELECT id, title FROM fater_practice_papers WHERE id=1")
    print("练习试卷:", cursor.fetchone())

    cursor.execute("SELECT id, title FROM fater_tasks WHERE id=1")
    print("任务:", cursor.fetchone())

    cursor.execute("SELECT name FROM fater_users WHERE type=0")
    print("管理员:", cursor.fetchone())

    print("\n✅ 数据编码修复成功！")

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    if 'conn' in locals():
        conn.close()
