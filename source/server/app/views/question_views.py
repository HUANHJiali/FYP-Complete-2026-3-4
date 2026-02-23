"""
题目管理视图
处理习题、选项等题目管理
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView
from comm.CommUtils import SysUtil, DateUtil
from utils.OperationLogger import OperationLogger


def _log_question_operation(request, operation_type, resource_id, resource_name, status=1):
    """记录题目操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='question',
                resource_id=str(resource_id),
                resource_name=resource_name,
                status=status,
                request=request
            )
    except Exception:
        pass


class PractisesView(BaseView):
    """习题管理视图"""

    def _check_teacher_permission(self, request):
        """检查教师权限（教师和管理员可访问）"""
        user = get_user_from_request(request)
        if not user:
            return False, BaseView.error('用户未登录')
        if user.type not in [0, 1]:  # 0-管理员, 1-教师
            return False, BaseView.error(f'权限不足：需要教师权限，当前角色：{self._get_role_name(user.type)}')
        return True, None

    @staticmethod
    def _get_role_name(user_type):
        """获取角色名称"""
        role_names = {0: '管理员', 1: '教师', 2: '学生'}
        return role_names.get(user_type, '未知')

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return self.get_page_infos(request)
        elif module == 'info':
            return self.get_info(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        # ✅ 安全检查：仅教师和管理员可添加/修改/删除题目
        allowed, error_response = self._check_teacher_permission(request)
        if not allowed:
            return error_response

        if module == 'add':
            return self.add_info(request)
        elif module == 'setanswer':
            return self.set_answer(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取指定 ID 的习题信息"""
        practise = models.Practises.objects.filter(id=request.GET.get('id')).first()

        if practise.type == 0:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
                'options': list(models.Options.objects.filter(practise__id=practise.id).values())
            })
        else:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
            })

    @staticmethod
    def get_page_infos(request):
        """分页查询习题信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        type = request.GET.get('type')
        projectId = request.GET.get('projectId')

        query = Q()
        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)
        if SysUtil.isExit(type):
            query = query & Q(type=int(type))
        if SysUtil.isExit(projectId):
            query = query & Q(project__id=int(projectId))

        # 使用select_related优化外键查询，避免N+1问题
        data = models.Practises.objects.filter(query).select_related('project').order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        # 获取当前页数据
        page_data = list(paginator.page(pageIndex))

        # 批量获取选项数量，避免循环中查询
        practise_ids = [item.id for item in page_data]
        option_counts = {}
        if practise_ids:
            option_counts_query = models.Options.objects.filter(
                practise_id__in=practise_ids
            ).values('practise_id').annotate(count=Count('id'))
            option_counts = {item['practise_id']: item['count'] for item in option_counts_query}

        for item in page_data:

            if item.type == 0:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': int(item.answer) if SysUtil.isExit(item.answer) else '',
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': option_counts.get(item.id, 0)
                })
            else:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': item.answer,
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': 0
                })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def add_info(request):
        """添加习题信息"""
        question_name = request.POST.get('name', '')[:50]
        question = models.Practises.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            project=models.Projects.objects.get(id=request.POST.get('projectId')),
            createTime=DateUtil.getNowDateTime()
        )
        _log_question_operation(request, 'create', question.id, question_name)
        return BaseView.success()

    @staticmethod
    def set_answer(request):
        """修改习题信息"""
        question_id = request.POST.get('id')
        question = models.Practises.objects.filter(id=question_id).first()
        question_name = question.name[:50] if question else question_id
        
        models.Practises.objects.filter(id=request.POST.get('id')).update(
            answer=request.POST.get('answer'),
            analyse=request.POST.get('analyse')
        )
        _log_question_operation(request, 'update', question_id, question_name)
        return BaseView.success()


class OptionsView(BaseView):
    """选项管理视图"""

    def _check_teacher_permission(self, request):
        """检查教师权限（教师和管理员可访问）"""
        user = get_user_from_request(request)
        if not user:
            return False, BaseView.error('用户未登录')
        if user.type not in [0, 1]:  # 0-管理员, 1-教师
            return False, BaseView.error(f'权限不足：需要教师权限，当前角色：{self._get_role_name(user.type)}')
        return True, None

    @staticmethod
    def _get_role_name(user_type):
        """获取角色名称"""
        role_names = {0: '管理员', 1: '教师', 2: '学生'}
        return role_names.get(user_type, '未知')

    def get(self, request, module, *args, **kwargs):
        if module == 'list':
            return self.get_list_by_practise_id(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        # ✅ 安全检查：仅教师和管理员可添加/修改选项
        allowed, error_response = self._check_teacher_permission(request)
        if not allowed:
            return error_response

        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_list_by_practise_id(request):
        """依据习题编号获取选项信息"""
        options = models.Options.objects.filter(practise__id=request.GET.get('practiseId'))
        return BaseView.successData(list(options.values()))

    @staticmethod
    def add_info(request):
        """添加选项信息"""
        models.Options.objects.create(
            name=request.POST.get('name'),
            practise=models.Practises.objects.get(id=request.POST.get('practiseId'))
        )
        return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改选项信息"""
        models.Options.objects.filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()
