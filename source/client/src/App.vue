<template>
  <div id="app">
    <router-view/>
    <LoadingSpinner 
      :visible="globalLoading" 
      :text="loadingText" 
      @close="closeLoading" />
    <NotificationToast 
      v-for="notification in notifications" 
      :key="notification.id"
      :visible="notification.visible"
      :type="notification.type"
      :title="notification.title"
      :message="notification.message"
      :duration="notification.duration"
      @close="removeNotification(notification.id)" />
  </div>
</template>

<script>
import LoadingSpinner from './components/LoadingSpinner.vue'
import NotificationToast from './components/NotificationToast.vue'

export default {
	name: 'App',
	components: {
		LoadingSpinner,
		NotificationToast
	},
  data() {
    return {
      globalLoading: false,
      loadingText: '加载中...',
      notifications: [],
      notificationId: 0
    }
  },
  methods: {
    showLoading(text = '加载中...') {
      this.loadingText = text
      this.globalLoading = true
    },
    hideLoading() {
      this.globalLoading = false
    },
    closeLoading() {
      this.globalLoading = false
    },
    showNotification(type, title, message, duration = 3000) {
      const id = ++this.notificationId
      const notification = {
        id,
        type,
        title,
        message,
        duration,
        visible: true
      }
      this.notifications.push(notification)
      
      // 自动移除通知
      setTimeout(() => {
        this.removeNotification(id)
      }, duration + 300)
    },
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },
    async checkBackendConnection() {
      try {
        const { checkBackendConnection, showConnectionError } = await import('./utils/connection-check.js')
        const isConnected = await checkBackendConnection()
        if (!isConnected) {
          // 延迟显示，避免干扰正常加载
          setTimeout(() => {
            showConnectionError()
          }, 2000)
        }
      } catch (error) {
        console.warn('连接检查失败:', error)
      }
    }
  },
  mounted() {
		// 将方法挂载到全局
		this.$root.$loading = {
			show: this.showLoading,
			hide: this.hideLoading
		}
		this.$root.$notify = {
			success: (title, message) => this.showNotification('success', title, message),
			warning: (title, message) => this.showNotification('warning', title, message),
			error: (title, message) => this.showNotification('error', title, message),
			info: (title, message) => this.showNotification('info', title, message)
		}
		
		// 开发环境：检查后端连接
		if (process.env.NODE_ENV === 'development') {
			this.checkBackendConnection()
		}
	},
}
</script>

<style>
#app {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #40a9ff 0%, #096dd9 100%);
}

/* 全局选择文本样式 */
::selection {
  background: rgba(24, 144, 255, 0.3);
  color: #333;
}

::-moz-selection {
  background: rgba(24, 144, 255, 0.3);
  color: #333;
}

/* 全局焦点样式 */
*:focus {
  outline: none;
}

*:focus-visible {
  outline: 2px solid #1890ff;
  outline-offset: 2px;
}

/* 全局过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* 全局按钮样式增强 */
.ivu-btn {
  transition: all 0.3s ease;
}

.ivu-btn:hover {
  transform: translateY(-1px);
}

/* 全局输入框样式增强 */
.ivu-input {
  transition: all 0.3s ease;
}

.ivu-input:focus {
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 全局表格样式增强 */
.ivu-table {
  border-radius: 8px;
  overflow: hidden;
}

.ivu-table th {
  background: #f8f9fa;
  font-weight: 600;
}

/* 全局模态框样式增强 */
.ivu-modal {
  border-radius: 12px;
  overflow: hidden;
}

.ivu-modal-header {
  background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
  color: #fff;
}

.ivu-modal-header-inner {
  color: #fff;
  font-weight: 600;
}

/* 全局分页样式增强 */
.ivu-page-item {
  border-radius: 6px;
  transition: all 0.3s ease;
}

.ivu-page-item:hover {
  background: #1890ff;
  color: #fff;
}

.ivu-page-item-active {
  background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
  border-color: #1890ff;
}

/* 全局标签样式增强 */
.ivu-tag {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.ivu-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计增强 */
@media (max-width: 768px) {
  .ivu-modal {
    margin: 10px;
    width: calc(100% - 20px) !important;
  }
  
  .ivu-table {
    font-size: 12px;
  }
  
  .ivu-btn {
    font-size: 12px;
    padding: 4px 8px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  body {
    background: #1a1a1a;
    color: #fff;
  }
  
  .ivu-card {
    background: #2a2a2a;
    border-color: #3a3a3a;
  }
  
  .ivu-table {
    background: #2a2a2a;
    color: #fff;
  }
  
  .ivu-table th {
    background: #3a3a3a;
    color: #fff;
  }
  
  .ivu-table td {
    border-color: #3a3a3a;
  }
}
</style>
