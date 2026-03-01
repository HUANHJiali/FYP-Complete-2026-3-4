"""
管理员用户管理相关视图

从 admin 视图中拆分用户管理逻辑，降低单文件复杂度。
"""

from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q

from app import models
from comm.BaseView import BaseView


class AdminUserView:
    """管理员用户管理接口集合"""

    @staticmethod
    def get_users(request):
        try:
            user_type = request.GET.get('type', '')
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')

            users_query = models.Users.objects.all().order_by('-createTime', '-id')

            if user_type:
                users_query = users_query.filter(type=int(user_type))

            if search:
                users_query = users_query.filter(
                    Q(userName__icontains=search) |
                    Q(name__icontains=search)
                )

            total = users_query.count()
            paginator = Paginator(users_query, size)
            users_page = paginator.get_page(page)

            users_data = []
            for user in users_page:
                user_data = {
                    'id': user.id,
                    'userName': user.userName,
                    'name': user.name,
                    'gender': user.gender,
                    'age': user.age,
                    'type': user.type,
                    'createTime': user.createTime.strftime('%Y-%m-%d %H:%M:%S') if user.createTime else '',
                    'lastLoginTime': user.lastLoginTime.strftime('%Y-%m-%d %H:%M:%S') if user.lastLoginTime else ''
                }

                if user.type == 1:
                    teacher = models.Teachers.objects.filter(user=user).first()
                    if teacher:
                        user_data.update({
                            'phone': teacher.phone,
                            'record': teacher.record,
                            'job': teacher.job
                        })
                elif user.type == 2:
                    student = models.Students.objects.filter(user=user).select_related('grade', 'college').first()
                    if student:
                        user_data.update({
                            'gradeId': student.grade.id if student.grade else None,
                            'gradeName': student.grade.name if student.grade else '',
                            'collegeId': student.college.id if student.college else None,
                            'collegeName': student.college.name if student.college else ''
                        })

                users_data.append(user_data)

            return BaseView.successData({
                'list': users_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取用户列表失败: {str(e)}')

    @staticmethod
    def manage_users(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                return AdminUserView.add_user(request)
            if action == 'update':
                return AdminUserView.update_user(request)
            if action == 'delete':
                return AdminUserView.delete_user(request)
            if action == 'disable':
                return AdminUserView.disable_user(request)

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'用户操作失败: {str(e)}')

    @staticmethod
    def add_user(request):
        try:
            user_type = int(request.POST.get('type'))
            user_name = request.POST.get('userName')
            password = request.POST.get('passWord') or '123456'
            name = request.POST.get('name')
            gender = request.POST.get('gender', '男')
            age = int(request.POST.get('age', 18))

            if models.Users.objects.filter(userName=user_name).exists():
                return BaseView.error('用户名已存在')

            user = models.Users.objects.create(
                userName=user_name,
                passWord=make_password(password),
                name=name,
                gender=gender,
                age=age,
                type=user_type
            )

            if user_type == 1:
                phone = request.POST.get('phone', '')
                record = request.POST.get('record', '')
                job = request.POST.get('job', '')
                models.Teachers.objects.create(
                    user=user,
                    phone=phone,
                    record=record,
                    job=job
                )
            elif user_type == 2:
                grade_id = request.POST.get('gradeId')
                college_id = request.POST.get('collegeId')
                grade = models.Grades.objects.filter(id=grade_id).first() if grade_id else None
                college = models.Colleges.objects.filter(id=college_id).first() if college_id else None
                models.Students.objects.create(
                    user=user,
                    grade=grade,
                    college=college
                )

            return BaseView.success('用户创建成功')
        except Exception as e:
            return BaseView.error(f'创建用户失败: {str(e)}')

    @staticmethod
    def update_user(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            user.name = request.POST.get('name', user.name)
            user.gender = request.POST.get('gender', user.gender)
            user.age = int(request.POST.get('age', user.age))
            user.save()

            if user.type == 1:
                teacher = models.Teachers.objects.filter(user=user).first()
                if teacher:
                    teacher.phone = request.POST.get('phone', teacher.phone)
                    teacher.record = request.POST.get('record', teacher.record)
                    teacher.job = request.POST.get('job', teacher.job)
                    teacher.save()
            elif user.type == 2:
                student = models.Students.objects.filter(user=user).select_related('grade', 'college').first()
                if student:
                    grade_id = request.POST.get('gradeId')
                    college_id = request.POST.get('collegeId')
                    if grade_id:
                        grade = models.Grades.objects.filter(id=grade_id).first()
                        if grade:
                            student.grade = grade
                    if college_id:
                        college = models.Colleges.objects.filter(id=college_id).first()
                        if college:
                            student.college = college
                    student.save()

            return BaseView.success('用户信息更新成功')
        except Exception as e:
            return BaseView.error(f'更新用户信息失败: {str(e)}')

    @staticmethod
    def delete_user(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            if user.type == 1:
                models.Teachers.objects.filter(user=user).delete()
            elif user.type == 2:
                models.Students.objects.filter(user=user).delete()

            user.delete()
            return BaseView.success('用户删除成功')
        except Exception as e:
            return BaseView.error(f'删除用户失败: {str(e)}')

    @staticmethod
    def disable_user(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            return BaseView.success('用户状态更新成功')
        except Exception as e:
            return BaseView.error(f'更新用户状态失败: {str(e)}')
