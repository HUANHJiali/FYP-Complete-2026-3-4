<template>
    <div class="notification-center">
        <div class="notification-header">
            <h3>通知中心</h3>
            <div class="notification-actions">
                <Button 
                    size="small" 
                    @click="markAllAsRead"
                    :disabled="!hasUnread"
                >
                    全部已读
                </Button>
                <Button 
                    size="small" 
                    type="text" 
                    @click="clearAll"
                    :disabled="notifications.length === 0"
                >
                    清空
                </Button>
            </div>
        </div>
        
        <div class="notification-tabs">
            <div 
                class="tab-item" 
                :class="{ active: activeTab === 'all' }"
                @click="activeTab = 'all'"
            >
                全部 ({{ notifications.length }})
            </div>
            <div 
                class="tab-item" 
                :class="{ active: activeTab === 'unread' }"
                @click="activeTab = 'unread'"
            >
                未读 ({{ unreadCount }})
            </div>
            <div 
                class="tab-item" 
                :class="{ active: activeTab === 'important' }"
                @click="activeTab = 'important'"
            >
                重要 ({{ importantCount }})
            </div>
        </div>
        
        <div class="notification-list">
            <div 
                v-for="notification in filteredNotifications" 
                :key="notification.id"
                class="notification-item"
                :class="{ 
                    unread: !notification.read,
                    important: notification.important,
                    [notification.type]: true
                }"
                @click="markAsRead(notification.id)"
            >
                <div class="notification-icon">
                    <Icon :type="getNotificationIcon(notification.type)" />
                </div>
                <div class="notification-content">
                    <div class="notification-title">
                        {{ notification.title }}
                        <span v-if="notification.important" class="important-badge">重要</span>
                    </div>
                    <div class="notification-message">{{ notification.message }}</div>
                    <div class="notification-meta">
                        <span class="notification-time">{{ formatTime(notification.time) }}</span>
                        <span v-if="notification.category" class="notification-category">
                            {{ notification.category }}
                        </span>
                    </div>
                </div>
                <div class="notification-actions">
                    <Button 
                        size="small" 
                        type="text" 
                        @click.stop="deleteNotification(notification.id)"
                    >
                        <Icon type="ios-close" />
                    </Button>
                </div>
            </div>
            
            <div v-if="filteredNotifications.length === 0" class="empty-state">
                <Icon type="ios-notifications-outline" />
                <p>暂无通知</p>
            </div>
        </div>
        
        <!-- 快速操作面板 -->
        <div class="quick-actions">
            <h4>快速操作</h4>
            <div class="action-buttons">
                <Button 
                    type="primary" 
                    size="small"
                    @click="createNotification"
                >
                    <Icon type="ios-add" />
                    发布通知
                </Button>
                <Button 
                    type="success" 
                    size="small"
                    @click="exportNotifications"
                >
                    <Icon type="ios-download" />
                    导出
                </Button>
                <Button 
                    type="warning" 
                    size="small"
                    @click="importNotifications"
                >
                    <Icon type="ios-upload" />
                    导入
                </Button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'NotificationCenter',
    data() {
        return {
            activeTab: 'all',
            notifications: [
                {
                    id: 1,
                    title: '系统维护通知',
                    message: '系统将于今晚22:00-24:00进行维护升级，期间可能影响正常使用。',
                    type: 'warning',
                    category: '系统',
                    important: true,
                    read: false,
                    time: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
                },
                {
                    id: 2,
                    title: '新功能上线',
                    message: '智能搜索功能已正式上线，支持多维度数据检索和智能推荐。',
                    type: 'success',
                    category: '功能',
                    important: false,
                    read: false,
                    time: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
                },
                {
                    id: 3,
                    title: '考试提醒',
                    message: '数学期中考试将于明天上午9:00开始，请提前做好准备。',
                    type: 'info',
                    category: '考试',
                    important: true,
                    read: true,
                    time: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4小时前
                },
                {
                    id: 4,
                    title: '数据备份完成',
                    message: '系统自动备份已完成，备份文件已保存到云端。',
                    type: 'success',
                    category: '系统',
                    important: false,
                    read: true,
                    time: new Date(Date.now() - 1000 * 60 * 60 * 6) // 6小时前
                },
                {
                    id: 5,
                    title: '安全提醒',
                    message: '检测到异常登录尝试，请及时检查账户安全。',
                    type: 'error',
                    category: '安全',
                    important: true,
                    read: false,
                    time: new Date(Date.now() - 1000 * 60 * 60 * 8) // 8小时前
                }
            ]
        }
    },
    computed: {
        filteredNotifications() {
            switch (this.activeTab) {
                case 'unread':
                    return this.notifications.filter(n => !n.read)
                case 'important':
                    return this.notifications.filter(n => n.important)
                default:
                    return this.notifications
            }
        },
        unreadCount() {
            return this.notifications.filter(n => !n.read).length
        },
        importantCount() {
            return this.notifications.filter(n => n.important).length
        },
        hasUnread() {
            return this.unreadCount > 0
        }
    },
    methods: {
        getNotificationIcon(type) {
            const icons = {
                success: 'ios-checkmark-circle',
                warning: 'ios-warning',
                error: 'ios-close-circle',
                info: 'ios-information-circle'
            }
            return icons[type] || 'ios-notifications'
        },
        formatTime(time) {
            const now = new Date()
            const diff = now - time
            const minutes = Math.floor(diff / (1000 * 60))
            const hours = Math.floor(diff / (1000 * 60 * 60))
            const days = Math.floor(diff / (1000 * 60 * 60 * 24))
            
            if (minutes < 60) {
                return `${minutes}分钟前`
            } else if (hours < 24) {
                return `${hours}小时前`
            } else {
                return `${days}天前`
            }
        },
        markAsRead(id) {
            const notification = this.notifications.find(n => n.id === id)
            if (notification) {
                notification.read = true
            }
        },
        markAllAsRead() {
            this.notifications.forEach(n => n.read = true)
        },
        deleteNotification(id) {
            const index = this.notifications.findIndex(n => n.id === id)
            if (index > -1) {
                this.notifications.splice(index, 1)
            }
        },
        clearAll() {
            this.notifications = []
        },
        createNotification() {
            // 模拟创建通知
            const newNotification = {
                id: Date.now(),
                title: '新通知',
                message: '这是一条新的通知消息。',
                type: 'info',
                category: '一般',
                important: false,
                read: false,
                time: new Date()
            }
            this.notifications.unshift(newNotification)
        },
        exportNotifications() {
            // 模拟导出功能
            const data = JSON.stringify(this.notifications, null, 2)
            const blob = new Blob([data], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'notifications.json'
            a.click()
            URL.revokeObjectURL(url)
        },
        importNotifications() {
            // 模拟导入功能
            const input = document.createElement('input')
            input.type = 'file'
            input.accept = '.json'
            input.onchange = (e) => {
                const file = e.target.files[0]
                if (file) {
                    const reader = new FileReader()
                    reader.onload = (e) => {
                        try {
                            const data = JSON.parse(e.target.result)
                            this.notifications = [...this.notifications, ...data]
                        } catch (error) {
                            console.error('导入失败:', error)
                        }
                    }
                    reader.readAsText(file)
                }
            }
            input.click()
        }
    }
}
</script>

<style scoped>
.notification-center {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}

.notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.notification-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 20px;
    font-weight: 600;
}

.notification-actions {
    display: flex;
    gap: 10px;
}

.notification-tabs {
    display: flex;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.tab-item {
    padding: 10px 20px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
    color: #7f8c8d;
    font-size: 14px;
}

.tab-item:hover {
    color: #2c3e50;
}

.tab-item.active {
    color: #667eea;
    border-bottom-color: #667eea;
}

.notification-list {
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 20px;
}

.notification-item {
    display: flex;
    align-items: flex-start;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    background: rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
    cursor: pointer;
    border-left: 4px solid transparent;
}

.notification-item:hover {
    background: rgba(255, 255, 255, 0.8);
    transform: translateX(5px);
}

.notification-item.unread {
    background: rgba(102, 126, 234, 0.05);
    border-left-color: #667eea;
}

.notification-item.important {
    border-left-color: #ff9900;
}

.notification-item.success {
    border-left-color: #19be6b;
}

.notification-item.warning {
    border-left-color: #ff9900;
}

.notification-item.error {
    border-left-color: #ed4014;
}

.notification-item.info {
    border-left-color: #2db7f5;
}

.notification-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    font-size: 18px;
}

.notification-item.success .notification-icon {
    background: rgba(25, 190, 107, 0.1);
    color: #19be6b;
}

.notification-item.warning .notification-icon {
    background: rgba(255, 153, 0, 0.1);
    color: #ff9900;
}

.notification-item.error .notification-icon {
    background: rgba(237, 64, 20, 0.1);
    color: #ed4014;
}

.notification-item.info .notification-icon {
    background: rgba(45, 183, 245, 0.1);
    color: #2db7f5;
}

.notification-content {
    flex: 1;
    margin-right: 15px;
}

.notification-title {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.important-badge {
    background: #ff9900;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: normal;
}

.notification-message {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 8px;
    line-height: 1.4;
}

.notification-meta {
    display: flex;
    gap: 15px;
    font-size: 12px;
}

.notification-time {
    color: #95a5a6;
}

.notification-category {
    color: #667eea;
    font-weight: 500;
}

.notification-actions {
    opacity: 0;
    transition: opacity 0.3s ease;
}

.notification-item:hover .notification-actions {
    opacity: 1;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #7f8c8d;
}

.empty-state i {
    font-size: 48px;
    margin-bottom: 15px;
    opacity: 0.5;
}

.empty-state p {
    margin: 0;
    font-size: 16px;
}

.quick-actions {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding-top: 20px;
}

.quick-actions h4 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 16px;
    font-weight: 600;
}

.action-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

/* 深色主题适配 */
.dark-theme .notification-center {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .notification-header h3,
.dark-theme .notification-title,
.dark-theme .quick-actions h4 {
    color: #fff;
}

.dark-theme .notification-message,
.dark-theme .notification-time,
.dark-theme .empty-state {
    color: #bdc3c7;
}

.dark-theme .notification-item {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .notification-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.dark-theme .notification-item.unread {
    background: rgba(102, 126, 234, 0.1);
}

.dark-theme .notification-tabs {
    border-bottom-color: rgba(255, 255, 255, 0.1);
}

.dark-theme .tab-item {
    color: #bdc3c7;
}

.dark-theme .tab-item:hover {
    color: #fff;
}

.dark-theme .quick-actions {
    border-top-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .notification-center {
        padding: 20px;
    }
    
    .notification-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
    
    .notification-tabs {
        flex-wrap: wrap;
    }
    
    .tab-item {
        padding: 8px 15px;
        font-size: 12px;
    }
    
    .notification-item {
        padding: 12px;
    }
    
    .notification-icon {
        width: 35px;
        height: 35px;
        font-size: 16px;
    }
    
    .action-buttons {
        flex-direction: column;
    }
}
</style>
