#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入练习题数据脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from app.models import *

def import_practice_questions():
    """导入练习题数据"""
    print("=== 开始导入练习题数据 ===")
    
    try:
        # 获取Java项目
        project = Projects.objects.get(id=3)  # Java项目
        
        # 练习题数据
        questions_data = [
            (1, 'JAVA数据类型不包括哪些', '13', '无', 0, '2024-11-03 15:45:34'),
            (2, 'Java源代码文件的后缀名是', '11', '无', 0, '2024-11-03 15:47:56'),
            (3, 'Java编译后文件的后缀名是', '6', '无', 0, '2024-11-03 15:48:08'),
            (4, '运行Java程序必须安装', '20', '无', 0, '2024-11-03 15:48:32'),
            (5, '面向对象的特征包括封装、继承、____', '多态', '无', 1, '2024-11-03 15:49:57'),
            (6, 'Java基本数据类型不包括 Boolean', '正确', 'boolean 是基础类型，Boolean 是它包装类型，属于引用类型', 2, '2024-11-03 15:51:56'),
            (7, '输入整数a、b，编程实现两个数字值互换', 'public static void main(String[] args) {\n\t\n\tScanner input = new Scanner(System.in);\n\t\n\tSystem.out.println("请输入数字 a: ");\n\tint a = input.nextInt();\n\t\n\n\tSystem.out.println("请输入数字 b: ");\n\tint b = input.nextInt();\n\t\n\tint c = a;\n\ta = b;\n\tb = c;\n\t\n\tSystem.out.println("交换后，a 的值是：" + a + ", b 的值是：" + b);\n}', '无', 3, '2024-11-03 15:56:06'),
            (8, '输入整数a、b，编程判断两个数字大小', 'public static void main(String[] args) {\n\t\n\tScanner input = new Scanner(System.in);\n\t\n\tSystem.out.println("请输入数字 a: ");\n\tint a = input.nextInt();\n\t\n\n\tSystem.out.println("请输入数字 b: ");\n\tint b = input.nextInt();\n\n\t\n\tif(a > b) {\n\t\t\n\t\tSystem.out.println("数字 a 大于数字 b");\n\t}else {\n\t\t\n\t\tSystem.out.println("数字 a 小于数字 b");\n\t}\n}', '无', 3, '2024-11-03 15:59:21'),
            (9, 'Java基本数据类型不包括', '3', '无', 0, '2024-11-03 16:01:11'),
            (10, 'Java支持跨平台开发', '正确', '无', 2, '2024-11-03 16:05:44'),
        ]
        
        # 创建练习题
        for question_id, name, answer, analyse, question_type, create_time in questions_data:
            question, created = Practises.objects.get_or_create(
                id=question_id,
                defaults={
                    'name': name,
                    'answer': answer,
                    'analyse': analyse,
                    'type': question_type,
                    'createTime': create_time,
                    'project': project
                }
            )
            if created:
                print(f"  创建练习题: {name}")
            else:
                print(f"  练习题已存在: {name}")
        
        # 创建选项数据
        print("创建选项数据...")
        options_data = [
            (1, 'int', 9),
            (2, 'double', 9),
            (3, 'String', 9),
            (4, 'boolean', 9),
            (5, 'java', 3),
            (6, 'class', 3),
            (7, 'exe', 3),
            (8, 'txt', 3),
            (9, 'txt', 2),
            (10, 'exe', 2),
            (11, 'java', 2),
            (12, 'class', 2),
            (13, 'number', 1),
            (14, 'int', 1),
            (15, 'float', 1),
            (16, 'double', 1),
            (17, 'Eclipse', 4),
            (18, 'IDEA', 4),
            (19, 'JDK', 4),
            (20, 'JRE', 4),
        ]
        
        for option_id, name, practise_id in options_data:
            try:
                practise = Practises.objects.get(id=practise_id)
                option, created = Options.objects.get_or_create(
                    id=option_id,
                    defaults={
                        'name': name,
                        'practise': practise
                    }
                )
                if created:
                    print(f"  创建选项: {name} (题目: {practise.name})")
                else:
                    print(f"  选项已存在: {name}")
            except Practises.DoesNotExist:
                print(f"  警告: 题目ID {practise_id} 不存在")
        
        print("✅ 练习题数据导入完成")
        return True
        
    except Exception as e:
        print(f"❌ 导入练习题数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_practice_questions()
    if success:
        print("\n🎉 练习题数据导入成功！")
    else:
        print("\n💥 练习题数据导入失败！")

