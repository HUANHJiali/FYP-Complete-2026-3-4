import time
from datetime import datetime

'''
系统处理工具类
'''
class SysUtil():

    '''
    检查指定的参数是否存在
    存在返回 True
    不存在返回 False
    '''
    def isExit(param):

        if (param == None) or (param == ''):
            return False
        else:
            return True

'''
时间处理工具类
'''
class DateUtil():

    def getNowDateTime(format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format, time.localtime())

    # 兼容旧代码：有些调用使用 getNowTime
    def getNowTime():
        return DateUtil.getNowDateTime()

    # 将字符串/时间戳安全地解析为 datetime，用于时长计算等
    def parseDateTime(value):
        if isinstance(value, datetime):
            return value
        if value is None:
            return datetime.now()
        try:
            s = str(value).strip()
        except Exception:
            return datetime.now()

        # 常见时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        # 尝试作为时间戳
        try:
            return datetime.fromtimestamp(float(s))
        except Exception:
            return datetime.now()