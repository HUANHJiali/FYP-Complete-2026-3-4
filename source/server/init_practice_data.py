#!/usr/bin/env python
"""
练习试卷系统数据初始化脚本
用于创建示例练习试卷和相关数据
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from app.models import Users, Projects, PracticePapers, PracticePaperQuestions, Practises

def init_practice_data():
    """初始化练习试卷系统数据"""
    print("=== 初始化练习试卷系统数据 ===")
    
    try:
        # 获取基础数据
        users = Users.objects.all()
        projects = Projects.objects.all()
        practises = Practises.objects.all()
        
        if not users.exists():
            print("❌ 没有用户数据，无法创建练习试卷")
            return False
        
        if not projects.exists():
            print("❌ 没有科目数据，无法创建练习试卷")
            return False
        
        if not practises.exists():
            print("❌ 没有题目数据，无法创建练习试卷")
            return False
        
        # 获取教师用户（type=1表示教师）
        teachers = users.filter(type=1)
        if not teachers.exists():
            print("⚠️  没有教师用户，使用第一个用户作为教师")
            teacher = users.first()
        else:
            teacher = teachers.first()
        
        print(f"使用教师: {teacher.name} ({teacher.userName})")
        
        # 创建练习试卷
        papers_data = [
            {
                'title': 'Java基础练习卷一',
                'description': '包含Java基础语法、数据类型、控制结构等知识点的综合练习，适合初学者。',
                'type': 'fixed',
                'difficulty': 'easy',
                'duration': 60,
                'totalScore': 100,
                'project': projects.filter(name__icontains='Java').first() or projects.first(),
                'questions_count': 5
            },
            {
                'title': 'C语言编程练习',
                'description': 'C语言基础语法和简单算法练习，涵盖指针、数组、函数等核心概念。',
                'type': 'timed',
                'difficulty': 'medium',
                'duration': 90,
                'totalScore': 120,
                'project': projects.filter(name__icontains='C语言').first() or projects.first(),
                'questions_count': 8
            },
            {
                'title': '数据结构基础练习',
                'description': '线性表、栈、队列、树等基础数据结构的理解和应用练习。',
                'type': 'fixed',
                'difficulty': 'hard',
                'duration': 120,
                'totalScore': 150,
                'project': projects.filter(name__icontains='数据结构').first() or projects.first(),
                'questions_count': 10
            },
            {
                'title': '算法思维训练',
                'description': '排序算法、查找算法、递归等基础算法的理解和应用。',
                'type': 'timed',
                'difficulty': 'hard',
                'duration': 150,
                'totalScore': 200,
                'project': projects.first(),
                'questions_count': 12
            }
        ]
        
        created_papers = []
        
        for paper_data in papers_data:
            # 创建练习试卷
            paper = PracticePapers.objects.create(
                title=paper_data['title'],
                description=paper_data['description'],
                type=paper_data['type'],
                difficulty=paper_data['difficulty'],
                duration=paper_data['duration'],
                totalScore=paper_data['totalScore'],
                project=paper_data['project'],
                teacher=teacher,
                createTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                isActive=True
            )
            
            print(f"✅ 创建练习试卷: {paper.title}")
            created_papers.append(paper)
            
            # 为试卷添加题目
            questions_count = min(paper_data['questions_count'], practises.count())
            selected_practises = practises.order_by('?')[:questions_count]  # 随机选择题目
            
            for i, practise in enumerate(selected_practises, 1):
                # 根据题目类型分配分数
                if practise.type == 0:  # 选择题
                    score = 20.0
                elif practise.type == 1:  # 填空题
                    score = 25.0
                elif practise.type == 2:  # 判断题
                    score = 15.0
                else:  # 编程题
                    score = 30.0
                
                PracticePaperQuestions.objects.create(
                    paper=paper,
                    practise=practise,
                    questionOrder=i,
                    score=score
                )
            
            print(f"   添加了 {questions_count} 道题目")
        
        print(f"\n🎉 成功创建 {len(created_papers)} 个练习试卷！")
        
        # 显示创建的试卷信息
        print("\n=== 创建的练习试卷 ===")
        for paper in created_papers:
            questions = PracticePaperQuestions.objects.filter(paper=paper)
            print(f"📝 {paper.title}")
            print(f"   类型: {paper.type} | 难度: {paper.difficulty} | 时长: {paper.duration}分钟")
            print(f"   总分: {paper.totalScore} | 题目数: {questions.count()}")
            print(f"   科目: {paper.project.name}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_practice_data():
    """清理练习试卷数据"""
    try:
        count = PracticePapers.objects.count()
        PracticePapers.objects.all().delete()
        print(f"✅ 清理了 {count} 个练习试卷")
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")

if __name__ == "__main__":
    print("开始初始化练习试卷系统数据...")
    
    # 检查是否已有数据
    existing_papers = PracticePapers.objects.count()
    if existing_papers > 0:
        print(f"⚠️  发现已有 {existing_papers} 个练习试卷")
        response = input("是否要清理现有数据并重新初始化？(y/N): ")
        if response.lower() == 'y':
            cleanup_practice_data()
        else:
            print("跳过初始化，保留现有数据")
            sys.exit(0)
    
    # 运行初始化
    success = init_practice_data()
    
    if success:
        print("\n🎉 练习试卷系统数据初始化完成！")
        print("现在可以启动前端应用来测试练习功能了。")
    else:
        print("\n💥 练习试卷系统数据初始化失败！")
        print("请检查错误信息并修复问题。")
    
    print("\n初始化完成！")
