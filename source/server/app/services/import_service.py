"""
批量导入服务
提供Excel/CSV文件的批量导入功能
"""
import pandas as pd
import os
from typing import List, Dict, Tuple, Any
from django.db import transaction
from django.contrib.auth.hashers import make_password
from app import models
from app.services.user_service import UserService
from app.validators import InputValidator


class ImportService:
    """批量导入服务类"""
    
    @staticmethod
    def import_students_from_excel(file_path: str) -> Tuple[int, int, List[str]]:
        """
        从Excel文件导入学生
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            tuple: (成功数量, 失败数量, 错误列表)
            
        Excel格式要求:
            - 列名: userName, name, passWord(可选), gender(可选), age(可选), collegeId, gradeId
            - 默认密码: 123456
            - 默认性别: M
            - 默认年龄: 18
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 验证必需的列
            required_columns = ['userName', 'name', 'collegeId', 'gradeId']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return 0, 0, [f"缺少必需的列: {', '.join(missing_columns)}"]
            
            success_count = 0
            fail_count = 0
            errors = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 获取数据
                        userName = str(row['userName']).strip()
                        name = str(row['name']).strip()
                        passWord = str(row.get('passWord', '123456')).strip() or '123456'
                        gender = str(row.get('gender', 'M')).strip() or 'M'
                        age = int(row.get('age', 18)) if pd.notna(row.get('age')) else 18
                        college_id = int(row['collegeId'])
                        grade_id = int(row['gradeId'])
                        
                        # 验证用户名
                        is_valid, error_msg = InputValidator.validate_username(userName)
                        if not is_valid:
                            errors.append(f"第{index+2}行: {error_msg}")
                            fail_count += 1
                            continue
                        
                        # 检查用户名是否已存在
                        if models.Users.objects.filter(userName=userName).exists():
                            errors.append(f"第{index+2}行: 用户名 '{userName}' 已存在")
                            fail_count += 1
                            continue
                        
                        # 验证学院和班级是否存在
                        try:
                            college = models.Colleges.objects.get(id=college_id)
                        except models.Colleges.DoesNotExist:
                            errors.append(f"第{index+2}行: 学院ID {college_id} 不存在")
                            fail_count += 1
                            continue
                        
                        try:
                            grade = models.Grades.objects.get(id=grade_id)
                        except models.Grades.DoesNotExist:
                            errors.append(f"第{index+2}行: 班级ID {grade_id} 不存在")
                            fail_count += 1
                            continue
                        
                        # 生成用户ID（Users的id是CharField）
                        import uuid
                        user_id = str(uuid.uuid4())[:20]  # 限制长度为20
                        
                        # 创建用户
                        user = models.Users.objects.create(
                            id=user_id,
                            userName=userName,
                            passWord=make_password(passWord),
                            name=name,
                            gender=gender,
                            age=age,
                            type=2  # 学生
                        )
                        
                        # 创建学生记录
                        models.Students.objects.create(
                            user=user,
                            college=college,
                            grade=grade
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"第{index+2}行: {str(e)}")
                        fail_count += 1
            
            return success_count, fail_count, errors
            
        except Exception as e:
            return 0, 0, [f"文件读取失败: {str(e)}"]
    
    @staticmethod
    def import_students_from_csv(file_path: str) -> Tuple[int, int, List[str]]:
        """
        从CSV文件导入学生
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            tuple: (成功数量, 失败数量, 错误列表)
        """
        try:
            # 读取CSV文件
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                # 尝试其他编码
                df = pd.read_csv(file_path, encoding='gbk')
            
            # 验证必需的列
            required_columns = ['userName', 'name', 'collegeId', 'gradeId']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return 0, 0, [f"缺少必需的列: {', '.join(missing_columns)}"]
            
            success_count = 0
            fail_count = 0
            errors = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 获取数据
                        userName = str(row['userName']).strip()
                        name = str(row['name']).strip()
                        passWord = str(row.get('passWord', '123456')).strip() or '123456'
                        gender = str(row.get('gender', 'M')).strip() or 'M'
                        age = int(row.get('age', 18)) if pd.notna(row.get('age')) else 18
                        college_id = int(row['collegeId'])
                        grade_id = int(row['gradeId'])
                        
                        # 验证用户名
                        is_valid, error_msg = InputValidator.validate_username(userName)
                        if not is_valid:
                            errors.append(f"第{index+2}行: {error_msg}")
                            fail_count += 1
                            continue
                        
                        # 检查用户名是否已存在
                        if models.Users.objects.filter(userName=userName).exists():
                            errors.append(f"第{index+2}行: 用户名 '{userName}' 已存在")
                            fail_count += 1
                            continue
                        
                        # 验证学院和班级是否存在
                        try:
                            college = models.Colleges.objects.get(id=college_id)
                        except models.Colleges.DoesNotExist:
                            errors.append(f"第{index+2}行: 学院ID {college_id} 不存在")
                            fail_count += 1
                            continue
                        
                        try:
                            grade = models.Grades.objects.get(id=grade_id)
                        except models.Grades.DoesNotExist:
                            errors.append(f"第{index+2}行: 班级ID {grade_id} 不存在")
                            fail_count += 1
                            continue
                        
                        # 生成用户ID（Users的id是CharField）
                        import uuid
                        user_id = str(uuid.uuid4())[:20]  # 限制长度为20
                        
                        # 创建用户
                        user = models.Users.objects.create(
                            id=user_id,
                            userName=userName,
                            passWord=make_password(passWord),
                            name=name,
                            gender=gender,
                            age=age,
                            type=2  # 学生
                        )
                        
                        # 创建学生记录
                        models.Students.objects.create(
                            user=user,
                            college=college,
                            grade=grade
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"第{index+2}行: {str(e)}")
                        fail_count += 1
            
            return success_count, fail_count, errors
            
        except Exception as e:
            return 0, 0, [f"文件读取失败: {str(e)}"]
    
    @staticmethod
    def download_student_template() -> str:
        """
        生成学生导入模板文件路径
        
        Returns:
            str: 模板文件路径
        """
        import tempfile
        from comm.CommUtils import DateUtil
        
        # 创建模板数据
        template_data = {
            'userName': ['student001', 'student002', 'student003'],
            'name': ['学生1', '学生2', '学生3'],
            'passWord': ['123456', '123456', '123456'],
            'gender': ['M', 'F', 'M'],
            'age': [18, 19, 20],
            'collegeId': [1, 1, 1],
            'gradeId': [1, 1, 1]
        }
        
        df = pd.DataFrame(template_data)
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        return temp_file.name
