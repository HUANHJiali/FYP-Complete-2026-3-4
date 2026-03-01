from datetime import datetime


LIFECYCLE_TEXT_MAP = {
    'not_started': '未开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'overdue': '已逾期',
    'disabled': '已禁用'
}


EXAM_STATUS_MAP = {
    'in_progress': 0,
    'not_started': 1,
    'completed': 2
}


def parse_datetime(dt_value):
    """解析日期时间，兼容常见字符串格式与 datetime 对象。"""
    if not dt_value:
        return None

    if isinstance(dt_value, datetime):
        return dt_value

    text = str(dt_value).strip()
    for fmt in [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d'
    ]:
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue

    return None


def status_text(status):
    return LIFECYCLE_TEXT_MAP.get(status, '未知状态')


def exam_status_code(status):
    return EXAM_STATUS_MAP.get(status, 1)


def resolve_exam_lifecycle(start_time=None, end_time=None, legacy_exam_time=None, now=None):
    now = now or datetime.now()
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)

    if start_dt or end_dt:
        if start_dt and now < start_dt:
            return 'not_started'
        if end_dt and now > end_dt:
            return 'completed'
        return 'in_progress'

    exam_dt = parse_datetime(legacy_exam_time)
    if exam_dt:
        return 'in_progress' if exam_dt <= now else 'not_started'

    return 'not_started'


def resolve_practice_lifecycle(log_status=None, is_active=True):
    if not is_active:
        return 'disabled'
    if log_status == 'completed':
        return 'completed'
    if log_status == 'in_progress':
        return 'in_progress'
    return 'not_started'


def resolve_task_lifecycle(log_status=None, deadline=None, is_active=True, now=None):
    if not is_active:
        return 'disabled'
    if log_status == 'completed':
        return 'completed'

    now = now or datetime.now()
    deadline_dt = parse_datetime(deadline)
    if deadline_dt and now > deadline_dt:
        return 'overdue'

    if log_status == 'in_progress':
        return 'in_progress'

    return 'not_started'
