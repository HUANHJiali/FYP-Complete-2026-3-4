#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查和创建任务系统需要的基础数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from app.models import *

def check_and_create_base_data():
    """检查和创建基础数据"""
    print("=== 检查和创建基础数据 ===")
    
    # 1. 检查并创建科目
    print("\n1. 检查科目数据...")
    try:
        project = Projects.objects.filter(id=1).first()
        if not project:
            print("创建数学科目...")
            project = Projects.objects.create(
                id=1,
                name='数学',
                description='数学基础课程',
                isActive=True
            )
            print(f"✅ 科目创建成功: {project.name}")
        else:
            print(f"✅ 科目已存在: {project.name}")
    except Exception as e:
        print(f"❌ 创建科目失败: {e}")
        return False
    
    # 2. 检查并创建年级
    print("\n2. 检查年级数据...")
    try:
        grade = Grades.objects.filter(id=1).first()
        if not grade:
            print("创建一年级...")
            grade = Grades.objects.create(
                id=1,
                name='一年级',
                description='小学一年级',
                isActive=True
            )
            print(f"✅ 年级创建成功: {grade.name}")
        else:
            print(f"✅ 年级已存在: {grade.name}")
    except Exception as e:
        print(f"❌ 创建年级失败: {e}")
        return False
    
    # 3. 检查并创建教师用户
    print("\n3. 检查教师用户...")
    try:
        teacher_user = Users.objects.filter(id='T2019092300001').first()
        if not teacher_user:
            print("创建教师用户...")
            teacher_user = Users.objects.create(
                id='T2019092300001',
                userName='teacher001',
                passWord='123456',
                name='张老师',
                gender='男',
                age=30,
                type=1  # 1-教师
            )
            print(f"✅ 教师用户创建成功: {teacher_user.name}")
        else:
            print(f"✅ 教师用户已存在: {teacher_user.name}")
    except Exception as e:
        print(f"❌ 创建教师用户失败: {e}")
        return False
    
    # 4. 检查并创建学生用户
    print("\n4. 检查学生用户...")
    try:
        student_user = Users.objects.filter(id='S2019092300001').first()
        if not student_user:
            print("创建学生用户...")
            student_user = Users.objects.create(
                id='S2019092300001',
                userName='student001',
                passWord='123456',
                name='李同学',
                gender='男',
                age=18,
                type=2  # 2-学生
            )
            print(f"✅ 学生用户创建成功: {student_user.name}")
        else:
            print(f"✅ 学生用户已存在: {student_user.name}")
    except Exception as e:
        print(f"❌ 创建学生用户失败: {e}")
        return False
    
    # 5. 检查并创建学生信息
    print("\n5. 检查学生信息...")
    try:
        student = Students.objects.filter(user__id='S2019092300001').first()
        if not student:
            print("创建学生信息...")
            student = Students.objects.create(
                user=student_user,
                grade=grade,
                isActive=True
            )
            print(f"✅ 学生信息创建成功: {student.user.name}")
        else:
            print(f"✅ 学生信息已存在: {student.user.name}")
    except Exception as e:
        print(f"❌ 创建学生信息失败: {e}")
        return False
    
    # 6. 检查并创建教师信息
    print("\n6. 检查教师信息...")
    try:
        teacher = Teachers.objects.filter(user__id='T2019092300001').first()
        if not teacher:
            print("创建教师信息...")
            teacher = Teachers.objects.create(
                user=teacher_user,
                phone='13800138000',
                record='本科',
                job='讲师'
            )
            print(f"✅ 教师信息创建成功: {teacher.user.name}")
        else:
            print(f"✅ 教师信息已存在: {teacher.user.name}")
    except Exception as e:
        print(f"❌ 创建教师信息失败: {e}")
        return False
    
    # 7. 检查并创建题目
    print("\n7. 检查题目数据...")
    try:
        question = Practises.objects.filter(id=1).first()
        if not question:
            print("创建测试题目...")
            question = Practises.objects.create(
                id=1,
                name='1 + 1 = ?',
                answer='A',
                analyse='这是一道基础数学题',
                type=0,  # 0-选择
                createTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                project=project
            )
            print(f"✅ 题目创建成功: {question.name}")
        else:
            print(f"✅ 题目已存在: {question.name}")
    except Exception as e:
        print(f"❌ 创建题目失败: {e}")
        return False
    
    # 8. 检查并创建题目选项
    print("\n8. 检查题目选项...")
    try:
        option = Options.objects.filter(practise=question).first()
        if not option:
            print("创建题目选项...")
            Options.objects.create(
                name='A',
                practise=question
            )
            Options.objects.create(
                name='B',
                practise=question
            )
            print("✅ 题目选项创建成功")
        else:
            print("✅ 题目选项已存在")
    except Exception as e:
        print(f"❌ 创建题目选项失败: {e}")
        return False
    
    # 9. 检查并创建任务题目关联
    print("\n9. 检查任务题目关联...")
    try:
        task_question = TaskQuestions.objects.filter(task_id=1, practise=question).first()
        if not task_question:
            print("创建任务题目关联...")
            task_question = TaskQuestions.objects.create(
                task_id=1,
                practise=question,
                questionOrder=1,
                score=10.0
            )
            print("✅ 任务题目关联创建成功")
        else:
            print("✅ 任务题目关联已存在")
    except Exception as e:
        print(f"❌ 创建任务题目关联失败: {e}")
        return False
    
    print("\n=== 基础数据检查和创建完成 ===")
    return True

if __name__ == "__main__":
    check_and_create_base_data()
