/**
 * 连接检查工具
 * 检查后端服务是否可用
 */
import http from './http.js'
import { Notice } from 'view-ui-plus'

/**
 * 检查后端连接
 * @returns {Promise<boolean>} 连接是否可用
 */
export async function checkBackendConnection() {
  try {
    // 尝试访问一个简单的API端点（不需要token）
    const response = await http.get('/projects/all/', {
      timeout: 5000  // 5秒超时
    })
    // 即使返回错误码，只要收到响应就说明连接正常
    return response !== undefined && response !== null
  } catch (error) {
    console.error('后端连接检查失败:', error)
    // 如果是网络错误，说明后端未启动
    if (error.message === 'Network Error' || error.code === 'ECONNABORTED') {
      return false
    }
    // 其他错误（如401、403）说明后端已启动，只是需要认证
    return true
  }
}

/**
 * 显示连接错误提示
 */
export function showConnectionError() {
  Notice.error({
    title: '无法连接到后端服务',
    desc: '请确认：\n1. 后端服务已启动（python manage.py runserver）\n2. 服务运行在 http://127.0.0.1:8000\n3. 防火墙未阻止连接\n4. 检查浏览器控制台获取详细信息',
    duration: 10
  })
}
