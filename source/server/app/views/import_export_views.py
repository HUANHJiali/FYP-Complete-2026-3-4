"""
简化版批量导入功能（不依赖pandas）
使用csv模块和openpyxl读取Excel文件
"""

import csv
import io
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from app import models
from app.permissions import get_user_from_request
from comm.CommUtils import DateUtil
from django.contrib.auth.hashers import make_password
from utils.OperationLogger import OperationLogger


def _log_import_operation(request, operation_type, module, detail, status=1):
    """记录导入导出操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name=module,
                resource_name=detail,
                status=status,
                request=request
            )
    except Exception:
        pass


def import_students(request):
    """
    批量导入学生信息（简化版）
    支持CSV格式
    """

    if request.method != 'POST':
        return JsonResponse({'code': 2, 'msg': '仅支持POST请求'})

    try:
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'code': 1, 'msg': '请选择要导入的文件'})

        file_ext = file.name.split('.')[-1].lower()
        if file_ext not in ['csv']:
            return JsonResponse({'code': 1, 'msg': '仅支持CSV文件格式'})

        # 读取CSV文件
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)

        # 读取表头
        headers = next(reader, None)
        if not headers:
            return JsonResponse({'code': 1, 'msg': 'CSV文件为空'})

        # 验证必需列
        required_columns = ['userName', 'name', 'gender', 'age', 'gradeName', 'collegeName']
        missing_columns = [col for col in required_columns if col not in headers]
        if missing_columns:
            return JsonResponse({
                'code': 1,
                'msg': f'缺少必需列: {", ".join(missing_columns)}'
            })

        # 获取列索引
        col_indices = {col: headers.index(col) for col in required_columns}

        success_count = 0
        error_count = 0
        errors = []

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    # 提取数据
                    userName = row[col_indices['userName']].strip()
                    name = row[col_indices['name']].strip()
                    gender = row[col_indices['gender']].strip()
                    age_str = row[col_indices['age']].strip()
                    gradeName = row[col_indices['gradeName']].strip()
                    collegeName = row[col_indices['collegeName']].strip()

                    # 验证必填字段
                    if not all([userName, name, gender, age_str, gradeName, collegeName]):
                        raise ValueError('必填字段不能为空')

                    # 验证年龄
                    try:
                        age = int(age_str)
                    except ValueError:
                        raise ValueError('年龄必须是数字')

                    # 检查学号是否已存在
                    if models.Users.objects.filter(userName=userName).exists():
                        errors.append(f'第{row_num}行: 学号{userName}已存在')
                        error_count += 1
                        continue

                    # 获取或创建学院
                    college, _ = models.Colleges.objects.get_or_create(
                        name=collegeName,
                        defaults={'createTime': DateUtil.getNowDateTime()}
                    )

                    # 获取或创建班级
                    grade, _ = models.Grades.objects.get_or_create(
                        name=gradeName,
                        defaults={'createTime': DateUtil.getNowDateTime()}
                    )

                    # 创建用户
                    user = models.Users.objects.create(
                        id=userName,
                        userName=userName,
                        passWord=make_password('123456'),
                        name=name,
                        gender=gender,
                        age=age,
                        type=2,
                        createTime=DateUtil.getNowDateTime()
                    )

                    # 创建学生信息
                    models.Students.objects.create(
                        user=user,
                        grade=grade,
                        college=college
                    )

                    success_count += 1

                except Exception as e:
                    errors.append(f'第{row_num}行: {str(e)}')
                    error_count += 1
                    continue

        _log_import_operation(request, 'import', 'student', f'批量导入学生{success_count}条')
        return JsonResponse({
            'code': 0,
            'msg': f'导入完成: 成功{success_count}条, 失败{error_count}条',
            'data': {
                'success': success_count,
                'error': error_count,
                'errors': errors[:10]
            }
        })

    except Exception as e:
        _log_import_operation(request, 'import', 'student', f'导入失败: {str(e)}', status=0)
        return JsonResponse({
            'code': 2,
            'msg': f'导入失败: {str(e)}'
        })


def export_students_template(request):
    """
    导出学生导入模板（CSV格式）
    """
    csv_content = """userName,name,gender,age,gradeName,collegeName
S2023001,张三,男,20,计科2101,计算机学院
S2023002,李四,女,19,计科2101,计算机学院
S2023003,王五,男,21,软件2201,软件学院"""

    response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=student_import_template.csv'
    return response
