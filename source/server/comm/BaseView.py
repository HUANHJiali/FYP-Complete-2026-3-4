'''
基础处理类，其他处理继承这个类
'''
import json

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')  # ✅ 安全修复：豁免 API 的 CSRF 检查（前后端分离项目）
class BaseView(View):

    '''
    转换分页查询信息
    '''
    def parasePage(pageIndex, pageSize, pageTotal, count, data):
        return {'pageIndex': pageIndex, 'pageSize': pageSize, 'pageTotal': pageTotal, 'count': count, 'data': data}

    '''
    成功响应信息
    '''
    def success(msg='处理成功'):
        resl = {'code': 0, 'msg': msg}
        return HttpResponse(json.dumps(resl, ensure_ascii=False), content_type='application/json; charset=utf-8')

    '''
    成功响应信息, 携带数据
    '''
    def successData(data, msg='处理成功'):
        resl = {'code': 0, 'msg': msg, 'data': data}
        return HttpResponse(json.dumps(resl, ensure_ascii=False), content_type='application/json; charset=utf-8')

    '''
    系统警告信息
    '''
    def warn(msg='操作异常，请重试'):
        resl = {'code': 1, 'msg': msg}
        return HttpResponse(json.dumps(resl, ensure_ascii=False), content_type='application/json; charset=utf-8')

    '''
    系统异常信息
    '''
    def error(msg='系统异常'):
        resl = {'code': 2, 'msg': msg}
        return HttpResponse(json.dumps(resl, ensure_ascii=False), content_type='application/json; charset=utf-8')