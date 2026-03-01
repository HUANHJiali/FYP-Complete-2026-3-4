export const lifecycleTextMap = {
  not_started: '未开始',
  in_progress: '进行中',
  completed: '已完成',
  overdue: '已逾期',
  disabled: '已禁用'
}

export const lifecycleTagMap = {
  not_started: 'warning',
  in_progress: 'processing',
  completed: 'success',
  overdue: 'error',
  disabled: 'default'
}

function mapLegacyExamStatus(status) {
  if (status === 0) return 'in_progress'
  if (status === 2) return 'completed'
  return 'not_started'
}

export function normalizeLifecycleStatus(item) {
  if (item && item.lifecycleStatus) {
    return item.lifecycleStatus
  }

  if (item && typeof item.status === 'number') {
    return mapLegacyExamStatus(item.status)
  }

  if (item && typeof item.status === 'string') {
    return item.status
  }

  return 'not_started'
}

export function getLifecycleText(status) {
  return lifecycleTextMap[status] || '未知状态'
}

export function getLifecycleTagType(status) {
  return lifecycleTagMap[status] || 'default'
}
