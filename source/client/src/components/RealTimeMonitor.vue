<template>
    <div class="real-time-monitor">
        <div class="monitor-header">
            <h3>实时监控</h3>
            <div class="monitor-status">
                <span class="status-indicator" :class="{ active: isOnline }"></span>
                {{ isOnline ? '在线' : '离线' }}
            </div>
        </div>
        
        <div class="monitor-grid">
            <!-- 在线用户 -->
            <div class="monitor-card">
                <div class="monitor-icon">
                    <Icon type="ios-people" />
                </div>
                <div class="monitor-content">
                    <div class="monitor-value">{{ onlineUsers }}</div>
                    <div class="monitor-label">在线用户</div>
                    <div class="monitor-trend">
                        <Icon type="ios-arrow-up" />
                        +{{ newUsers }} 新用户
                    </div>
                </div>
            </div>
            
            <!-- 活跃考试 -->
            <div class="monitor-card">
                <div class="monitor-icon">
                    <Icon type="ios-document" />
                </div>
                <div class="monitor-content">
                    <div class="monitor-value">{{ activeExams }}</div>
                    <div class="monitor-label">活跃考试</div>
                    <div class="monitor-trend">
                        <Icon type="ios-time" />
                        {{ examProgress }}% 完成
                    </div>
                </div>
            </div>
            
            <!-- 系统负载 -->
            <div class="monitor-card">
                <div class="monitor-icon">
                    <Icon type="ios-speedometer" />
                </div>
                <div class="monitor-content">
                    <div class="monitor-value">{{ systemLoad }}%</div>
                    <div class="monitor-label">系统负载</div>
                    <div class="monitor-trend">
                        <Icon :type="loadTrend === 'up' ? 'ios-arrow-up' : 'ios-arrow-down'" />
                        {{ loadChange }}%
                    </div>
                </div>
            </div>
            
            <!-- 响应时间 -->
            <div class="monitor-card">
                <div class="monitor-icon">
                    <Icon type="ios-timer" />
                </div>
                <div class="monitor-content">
                    <div class="monitor-value">{{ responseTime }}ms</div>
                    <div class="monitor-label">响应时间</div>
                    <div class="monitor-trend">
                        <Icon :type="responseTrend === 'up' ? 'ios-arrow-up' : 'ios-arrow-down'" />
                        {{ responseChange }}ms
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 实时活动流 -->
        <div class="activity-stream">
            <h4>实时活动</h4>
            <div class="stream-container">
                <div 
                    v-for="activity in recentActivities" 
                    :key="activity.id"
                    class="stream-item"
                    :class="activity.type"
                >
                    <div class="stream-time">{{ activity.time }}</div>
                    <div class="stream-icon">
                        <Icon :type="activity.icon" />
                    </div>
                    <div class="stream-content">
                        <div class="stream-title">{{ activity.title }}</div>
                        <div class="stream-desc">{{ activity.description }}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 系统状态指示器 -->
        <div class="system-status">
            <div class="status-item" v-for="status in systemStatus" :key="status.name">
                <div class="status-name">{{ status.name }}</div>
                <div class="status-bar">
                    <div 
                        class="status-fill" 
                        :style="{ width: status.value + '%', background: status.color }"
                    ></div>
                </div>
                <div class="status-value">{{ status.value }}%</div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'RealTimeMonitor',
    data() {
        return {
            isOnline: true,
            onlineUsers: 156,
            newUsers: 12,
            activeExams: 8,
            examProgress: 67,
            systemLoad: 45,
            loadChange: 3,
            loadTrend: 'up',
            responseTime: 120,
            responseChange: -15,
            responseTrend: 'down',
            recentActivities: [
                {
                    id: 1,
                    time: '刚刚',
                    type: 'success',
                    icon: 'ios-checkmark-circle',
                    title: '张三完成数学考试',
                    description: '得分：85分'
                },
                {
                    id: 2,
                    time: '1分钟前',
                    type: 'info',
                    icon: 'ios-person-add',
                    title: '新用户注册',
                    description: '李四加入系统'
                },
                {
                    id: 3,
                    time: '2分钟前',
                    type: 'warning',
                    icon: 'ios-warning',
                    title: '系统警告',
                    description: 'database连接延迟'
                },
                {
                    id: 4,
                    time: '3分钟前',
                    type: 'success',
                    icon: 'ios-document',
                    title: '考试创建成功',
                    description: '物理期中考试'
                },
                {
                    id: 5,
                    time: '5分钟前',
                    type: 'info',
                    icon: 'ios-cloud-upload',
                    title: '数据备份完成',
                    description: '自动备份成功'
                }
            ],
            systemStatus: [
                { name: 'CPU使用率', value: 45, color: '#19be6b' },
                { name: '内存使用率', value: 67, color: '#2db7f5' },
                { name: '磁盘使用率', value: 23, color: '#ff9900' },
                { name: '网络使用率', value: 34, color: '#667eea' }
            ]
        }
    },
    mounted() {
        this.startMonitoring()
    },
    beforeUnmount() {
        this.stopMonitoring()
    },
    methods: {
        startMonitoring() {
            // 模拟实时数据更新
            this.monitorInterval = setInterval(() => {
                this.updateData()
            }, 5000)
        },
        stopMonitoring() {
            if (this.monitorInterval) {
                clearInterval(this.monitorInterval)
            }
        },
        updateData() {
            // 模拟数据变化
            this.onlineUsers += Math.floor(Math.random() * 10) - 5
            this.onlineUsers = Math.max(100, Math.min(200, this.onlineUsers))
            
            this.systemLoad += Math.floor(Math.random() * 10) - 5
            this.systemLoad = Math.max(20, Math.min(80, this.systemLoad))
            
            this.responseTime += Math.floor(Math.random() * 20) - 10
            this.responseTime = Math.max(80, Math.min(200, this.responseTime))
            
            // 更新系统状态
            this.systemStatus.forEach(status => {
                status.value += Math.floor(Math.random() * 10) - 5
                status.value = Math.max(10, Math.min(90, status.value))
            })
        }
    }
}
</script>

<style scoped>
.real-time-monitor {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}

.monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.monitor-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 20px;
    font-weight: 600;
}

.monitor-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #7f8c8d;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ed4014;
    animation: pulse 2s infinite;
}

.status-indicator.active {
    background: #19be6b;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.monitor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.monitor-card {
    background: rgba(255, 255, 255, 0.5);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
}

.monitor-card:hover {
    background: rgba(255, 255, 255, 0.8);
    transform: translateY(-2px);
}

.monitor-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
    margin-right: 15px;
}

.monitor-content {
    flex: 1;
}

.monitor-value {
    font-size: 24px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 5px;
}

.monitor-label {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 8px;
}

.monitor-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #19be6b;
}

.activity-stream {
    margin-bottom: 25px;
}

.activity-stream h4 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 16px;
    font-weight: 600;
}

.stream-container {
    max-height: 300px;
    overflow-y: auto;
}

.stream-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
}

.stream-item:hover {
    background: rgba(255, 255, 255, 0.8);
}

.stream-item.success {
    border-left: 4px solid #19be6b;
}

.stream-item.info {
    border-left: 4px solid #2db7f5;
}

.stream-item.warning {
    border-left: 4px solid #ff9900;
}

.stream-item.error {
    border-left: 4px solid #ed4014;
}

.stream-time {
    font-size: 12px;
    color: #7f8c8d;
    min-width: 60px;
    margin-right: 10px;
}

.stream-icon {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    font-size: 14px;
}

.stream-item.success .stream-icon {
    background: rgba(25, 190, 107, 0.1);
    color: #19be6b;
}

.stream-item.info .stream-icon {
    background: rgba(45, 183, 245, 0.1);
    color: #2db7f5;
}

.stream-item.warning .stream-icon {
    background: rgba(255, 153, 0, 0.1);
    color: #ff9900;
}

.stream-item.error .stream-icon {
    background: rgba(237, 64, 20, 0.1);
    color: #ed4014;
}

.stream-content {
    flex: 1;
}

.stream-title {
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 4px;
}

.stream-desc {
    font-size: 12px;
    color: #7f8c8d;
}

.system-status {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
}

.status-item {
    background: rgba(255, 255, 255, 0.5);
    border-radius: 8px;
    padding: 15px;
}

.status-name {
    font-size: 12px;
    color: #7f8c8d;
    margin-bottom: 8px;
}

.status-bar {
    height: 6px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 5px;
}

.status-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.status-value {
    font-size: 12px;
    color: #2c3e50;
    font-weight: 500;
    text-align: right;
}

/* 深色主题适配 */
.dark-theme .real-time-monitor {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .monitor-header h3,
.dark-theme .activity-stream h4,
.dark-theme .monitor-value,
.dark-theme .stream-title,
.dark-theme .status-value {
    color: #fff;
}

.dark-theme .monitor-status,
.dark-theme .monitor-label,
.dark-theme .stream-time,
.dark-theme .stream-desc,
.dark-theme .status-name {
    color: #bdc3c7;
}

.dark-theme .monitor-card,
.dark-theme .stream-item,
.dark-theme .status-item {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .monitor-card:hover,
.dark-theme .stream-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.dark-theme .status-bar {
    background: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .monitor-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .system-status {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .monitor-card {
        padding: 15px;
    }
    
    .monitor-icon {
        width: 40px;
        height: 40px;
        font-size: 16px;
    }
    
    .monitor-value {
        font-size: 20px;
    }
}
</style>
