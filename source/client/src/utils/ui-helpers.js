/**
 * UI辅助函数
 * 提供统一的UI交互方法
 */

/**
 * 显示成功提示
 */
export function showSuccess(message, title = '成功', duration = 3000) {
  if (window.Vue && window.Vue.$Message) {
    window.Vue.$Message.success({
      content: message,
      duration: duration / 1000
    })
  } else {
    console.log(`[成功] ${title}: ${message}`)
  }
}

/**
 * 显示错误提示
 */
export function showError(message, title = '错误', duration = 3000) {
  if (window.Vue && window.Vue.$Message) {
    window.Vue.$Message.error({
      content: message,
      duration: duration / 1000
    })
  } else {
    console.error(`[错误] ${title}: ${message}`)
  }
}

/**
 * 显示警告提示
 */
export function showWarning(message, title = '警告', duration = 3000) {
  if (window.Vue && window.Vue.$Message) {
    window.Vue.$Message.warning({
      content: message,
      duration: duration / 1000
    })
  } else {
    console.warn(`[警告] ${title}: ${message}`)
  }
}

/**
 * 显示信息提示
 */
export function showInfo(message, title = '提示', duration = 3000) {
  if (window.Vue && window.Vue.$Message) {
    window.Vue.$Message.info({
      content: message,
      duration: duration / 1000
    })
  } else {
    console.info(`[提示] ${title}: ${message}`)
  }
}

/**
 * 显示确认对话框
 */
export function showConfirm(title, content, onOk, onCancel) {
  if (window.Vue && window.Vue.$Modal) {
    window.Vue.$Modal.confirm({
      title: title,
      content: content,
      onOk: onOk,
      onCancel: onCancel
    })
  } else {
    if (confirm(`${title}\n\n${content}`)) {
      onOk && onOk()
    } else {
      onCancel && onCancel()
    }
  }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 格式化时间
 */
export function formatTime(timeStr, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

/**
 * 格式化相对时间
 */
export function formatRelativeTime(timeStr) {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 7) {
    return formatTime(timeStr, 'YYYY-MM-DD')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

/**
 * 复制到剪贴板
 */
export function copyToClipboard(text) {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text).then(() => {
      showSuccess('已复制到剪贴板')
      return true
    }).catch(() => {
      showError('复制失败')
      return false
    })
  } else {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      document.body.removeChild(textarea)
      showSuccess('已复制到剪贴板')
      return Promise.resolve(true)
    } catch (err) {
      document.body.removeChild(textarea)
      showError('复制失败')
      return Promise.resolve(false)
    }
  }
}

/**
 * 防抖装饰器
 */
export function debounceDecorator(func, wait = 300) {
  let timeout
  return function(...args) {
    const context = this
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      func.apply(context, args)
    }, wait)
  }
}

/**
 * 节流装饰器
 */
export function throttleDecorator(func, limit = 300) {
  let inThrottle
  return function(...args) {
    const context = this
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

