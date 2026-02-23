#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入原始数据脚本
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from app.models import *

def import_original_data():
    """导入原始数据"""
    print("=== 开始导入原始数据 ===")
    
    try:
        # 1. 创建科目
        print("1. 创建科目...")
        projects_data = [
            (1, 'C语言', '2024-11-02 11:18:03'),
            (2, 'Python', '2024-11-02 11:18:12'),
            (3, 'Java', '2024-11-02 11:18:21'),
            (4, '软件测试', '2024-11-02 11:18:38')
        ]
        
        for project_id, name, create_time in projects_data:
            project, created = Projects.objects.get_or_create(
                id=project_id,
                defaults={'name': name, 'createTime': create_time}
            )
            if created:
                print(f"  创建科目: {name}")
            else:
                print(f"  科目已存在: {name}")
        
        # 2. 创建学院
        print("2. 创建学院...")
        colleges_data = [
            (1, '软件工程', '2024-11-02 11:07:57'),
            (2, '信息工程', '2024-11-02 11:08:07')
        ]
        
        for college_id, name, create_time in colleges_data:
            college, created = Colleges.objects.get_or_create(
                id=college_id,
                defaults={'name': name, 'createTime': create_time}
            )
            if created:
                print(f"  创建学院: {name}")
            else:
                print(f"  学院已存在: {name}")
        
        # 3. 创建班级
        print("3. 创建班级...")
        grades_data = [
            (1, '一年级一班', '2024-11-02 11:08:22'),
            (2, '一年级二班', '2024-11-02 11:08:31'),
            (3, '二年级一班', '2024-11-02 11:08:42'),
            (4, '二年级二班', '2024-11-02 11:08:48'),
            (5, '三年级一班', '2024-11-02 11:08:57'),
            (6, '三年级二班', '2024-11-02 11:09:02')
        ]
        
        for grade_id, name, create_time in grades_data:
            grade, created = Grades.objects.get_or_create(
                id=grade_id,
                defaults={'name': name, 'createTime': create_time}
            )
            if created:
                print(f"  创建班级: {name}")
            else:
                print(f"  班级已存在: {name}")
        
        # 4. 创建用户
        print("4. 创建用户...")
        users_data = [
            ('1', 'python222', '123456', '张三丰', '男', 45, 0),
            ('S2019092300001', 'zhangwuji', 'zhangwuji', '张无忌', '男', 23, 2),
            ('S2019092300002', 'songqingshu', 'songqingshu', '宋青书', '男', 23, 2),
            ('S2019092300003', 'zhouzhiruo', 'zhouzhiruo', '周芷若', '女', 23, 2),
            ('S2019092300004', 'zhujiuzhen', 'zhujiuzhen', '朱九真', '女', 19, 2),
            ('T2010012000001', 'zhuchanglin', 'zhuchanglin', '朱长龄', '男', 35, 1),
            ('T2010012000002', 'songyuanqiao', 'songyuanqiao', '宋远桥', '男', 42, 1)
        ]
        
        for user_id, username, password, name, gender, age, user_type in users_data:
            user, created = Users.objects.get_or_create(
                id=user_id,
                defaults={
                    'userName': username,
                    'passWord': password,
                    'name': name,
                    'gender': gender,
                    'age': age,
                    'type': user_type
                }
            )
            if created:
                print(f"  创建用户: {name} ({username})")
            else:
                print(f"  用户已存在: {name} ({username})")
        
        # 5. 创建学生信息
        print("5. 创建学生信息...")
        students_data = [
            ('S2019092300001', 1, 3),  # 张无忌 - 软件工程 - 二年级一班
            ('S2019092300002', 1, 3),  # 宋青书 - 软件工程 - 二年级一班
            ('S2019092300003', 1, 4),  # 周芷若 - 软件工程 - 二年级二班
            ('S2019092300004', 1, 1),  # 朱九真 - 软件工程 - 一年级一班
        ]
        
        for user_id, college_id, grade_id in students_data:
            user = Users.objects.get(id=user_id)
            college = Colleges.objects.get(id=college_id)
            grade = Grades.objects.get(id=grade_id)
            
            student, created = Students.objects.get_or_create(
                user=user,
                defaults={'college': college, 'grade': grade}
            )
            if created:
                print(f"  创建学生信息: {user.name}")
            else:
                print(f"  学生信息已存在: {user.name}")
        
        # 6. 创建教师信息
        print("6. 创建教师信息...")
        teachers_data = [
            ('T2010012000001', '30920390', '本科', '助理讲师'),
            ('T2010012000002', '30920391', '研究生', '普通教员')
        ]
        
        for user_id, phone, record, job in teachers_data:
            user = Users.objects.get(id=user_id)
            
            teacher, created = Teachers.objects.get_or_create(
                user=user,
                defaults={'phone': phone, 'record': record, 'job': job}
            )
            if created:
                print(f"  创建教师信息: {user.name}")
            else:
                print(f"  教师信息已存在: {user.name}")
        
        print("✅ 原始数据导入完成")
        return True
        
    except Exception as e:
        print(f"❌ 导入原始数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_original_data()
    if success:
        print("\n🎉 原始数据导入成功！")
    else:
        print("\n💥 原始数据导入失败！")

