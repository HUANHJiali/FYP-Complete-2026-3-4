#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化默认用户账户
根据 DOCKER_DEPLOYMENT.md 中的默认账户配置创建
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from app.models import Users, Teachers, Students, Colleges, Grades

def init_default_users():
    """初始化默认用户账户"""
    print("=== 初始化默认用户账户 ===")
    
    # 默认账户配置
    default_users = [
        {
            'id': 'ADMIN001',
            'userName': 'admin',
            'passWord': '123456',
            'name': '系统管理员',
            'gender': '男',
            'age': 30,
            'type': 0  # 0-管理员
        },
        {
            'id': 'TEACHER001',
            'userName': 'teacher',
            'passWord': '123456',
            'name': '教师账户',
            'gender': '男',
            'age': 35,
            'type': 1  # 1-教师
        },
        {
            'id': 'STUDENT001',
            'userName': 'student',
            'passWord': '123456',
            'name': '学生账户',
            'gender': '男',
            'age': 20,
            'type': 2  # 2-学生
        }
    ]
    
    for user_data in default_users:
        try:
            # 检查用户是否已存在（按用户名）
            existing_user = Users.objects.filter(userName=user_data['userName']).first()
            
            if existing_user:
                # 如果存在，更新信息（使用加密密码）
                print(f"⚠️  用户已存在: {user_data['userName']} ({existing_user.name})")
                existing_user.id = user_data['id']
                existing_user.passWord = make_password(user_data['passWord'])
                existing_user.name = user_data['name']
                existing_user.gender = user_data['gender']
                existing_user.age = user_data['age']
                existing_user.type = user_data['type']
                existing_user.save()
                print(f"✅ 用户信息已更新: {user_data['userName']}")
            else:
                # 如果不存在，创建新用户（使用加密密码）
                user_data_copy = user_data.copy()
                user_data_copy['passWord'] = make_password(user_data['passWord'])
                user = Users.objects.create(**user_data_copy)
                print(f"✅ 用户创建成功: {user_data['userName']} ({user_data['name']})")
        except Exception as e:
            print(f"❌ 创建/更新用户失败 {user_data['userName']}: {e}")
            return False
    
    # 验证创建结果
    print("\n=== 验证默认账户 ===")
    default_usernames = ['admin', 'teacher', 'student']
    for username in default_usernames:
        user = Users.objects.filter(userName=username).first()
        if user:
            role_map = {0: '管理员', 1: '教师', 2: '学生'}
            role = role_map.get(user.type, '未知')
            print(f"✅ {username}: {user.name} ({role})")
        else:
            print(f"❌ {username}: 未找到")
    
    # 创建教师和学生关联信息
    print("\n=== 创建教师和学生关联信息 ===")
    
    # 获取或创建默认学院和年级
    try:
        college = Colleges.objects.filter(id=1).first()
        if not college:
            print("⚠️  未找到默认学院，请先创建学院数据")
            college = Colleges.objects.first()
            if not college:
                print("❌ 数据库中没有任何学院数据，无法创建学生信息")
                return False
        
        grade = Grades.objects.filter(id=1).first()
        if not grade:
            print("⚠️  未找到默认年级，请先创建年级数据")
            grade = Grades.objects.first()
            if not grade:
                print("❌ 数据库中没有任何年级数据，无法创建学生信息")
                return False
        
        # 创建教师信息
        teacher_user = Users.objects.filter(userName='teacher').first()
        if teacher_user:
            teacher, created = Teachers.objects.get_or_create(
                user=teacher_user,
                defaults={
                    'phone': '13800000000',
                    'record': '本科',
                    'job': '讲师'
                }
            )
            if created:
                print(f"✅ 教师信息创建成功: {teacher_user.name}")
            else:
                print(f"✅ 教师信息已存在: {teacher_user.name}")
        
        # 创建学生信息
        student_user = Users.objects.filter(userName='student').first()
        if student_user:
            student, created = Students.objects.get_or_create(
                user=student_user,
                defaults={
                    'college': college,
                    'grade': grade
                }
            )
            if created:
                print(f"✅ 学生信息创建成功: {student_user.name}")
            else:
                print(f"✅ 学生信息已存在: {student_user.name}")
        
    except Exception as e:
        print(f"❌ 创建教师/学生关联信息失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n=== 默认用户账户初始化完成 ===")
    return True

if __name__ == "__main__":
    success = init_default_users()
    sys.exit(0 if success else 1)

