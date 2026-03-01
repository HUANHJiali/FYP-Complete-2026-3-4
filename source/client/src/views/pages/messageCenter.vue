<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-mail" class="header-icon" />
                <div class="header-text">
                    <h2>消息中心</h2>
                    <p>接收和管理员的重要通知和消息</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalMessages }}</div>
                    <div class="stat-label">总消息数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ unreadCount }}</div>
                    <div class="stat-label">未读消息</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ todayMessages }}</div>
                    <div class="stat-label">今日消息</div>
                </div>
            </div>
        </div>

        <Row :gutter="24" class="message-container">
            <Col span="8">
                <Card class="message-list-card animate-fade-in-up delay-100">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-list" class="title-icon" />
                            <span>消息列表</span>
                            <div class="title-actions">
                                <Button 
                                    type="text" 
                                    @click="markAllAsRead"
                                    :disabled="unreadCount === 0"
                                    class="action-btn">
                                    <Icon type="ios-checkmark-circle" />
                                    全部已读
                                </Button>
                            </div>
                        </div>
                    </template>
                    
                    <div class="message-filters">
                        <Select 
                            v-model="filterType" 
                            placeholder="消息类型"
                            class="filter-select"
                            @on-change="filterMessages">
                            <Option value="">全部类型</Option>
                            <Option value="notice">通知公告</Option>
                            <Option value="exam">考试相关</Option>
                            <Option value="task">任务通知</Option>
                            <Option value="system">系统消息</Option>
                        </Select>
                    </div>

                    <div class="message-list">
                        <div 
                            v-for="message in filteredMessages" 
                            :key="message.id"
                            class="message-item"
                            :class="{ 
                                'unread': !message.isRead,
                                'selected': selectedMessage && selectedMessage.id === message.id
                            }"
                            @click="selectMessage(message)">
                            <div class="message-header">
                                <div class="message-type">
                                    <Tag :type="getMessageTypeTag(message.type)" size="small">
                                        {{ getMessageTypeText(message.type) }}
                                    </Tag>
                                </div>
                                <div class="message-time">
                                    {{ formatTime(message.sendTime) }}
                                </div>
                            </div>
                            <div class="message-title">
                                {{ message.title }}
                            </div>
                            <div class="message-preview">
                                {{ message.content.substring(0, 50) }}...
                            </div>
                            <div class="message-status">
                                <Icon 
                                    v-if="!message.isRead" 
                                    type="ios-radio-button-on" 
                                    color="#ff4757" 
                                    size="12" />
                                <span v-else class="read-indicator">已读</span>
                            </div>
                        </div>
                    </div>

                    <div v-if="filteredMessages.length === 0" class="empty-state">
                        <Icon type="ios-mail-open" size="48" color="#ccc" />
                        <p>暂无消息</p>
                    </div>
                </Card>
            </Col>

            <Col span="16">
                <Card class="message-detail-card animate-fade-in-up delay-200">
                    <template #title>
                        <div class="card-title">
                            <Icon type="ios-document" class="title-icon" />
                            <span>消息详情</span>
                        </div>
                    </template>
                    
                    <div v-if="selectedMessage" class="message-detail">
                        <div class="detail-header">
                            <div class="message-meta">
                                <div class="message-title-large">
                                    {{ selectedMessage.title }}
                                </div>
                                <div class="message-info">
                                    <span class="sender">
                                        <Icon type="ios-person" />
                                        发送者: {{ selectedMessage.sender }}
                                    </span>
                                    <span class="time">
                                        <Icon type="ios-time" />
                                        发送时间: {{ formatTime(selectedMessage.sendTime) }}
                                    </span>
                                    <span class="type">
                                        <Icon type="ios-pricetag" />
                                        类型: {{ getMessageTypeText(selectedMessage.type) }}
                                    </span>
                                </div>
                            </div>
                            <div class="message-actions">
                                <Button 
                                    v-if="!selectedMessage.isRead"
                                    type="primary" 
                                    @click="markAsRead(selectedMessage.id)"
                                    class="action-btn">
                                    <Icon type="ios-checkmark" />
                                    标记已读
                                </Button>
                                <Button 
                                    type="default" 
                                    @click="forwardMessage(selectedMessage)"
                                    class="action-btn">
                                    <Icon type="ios-share" />
                                    转发
                                </Button>
                                <Button 
                                    type="error" 
                                    @click="deleteMessage(selectedMessage.id)"
                                    class="action-btn">
                                    <Icon type="ios-trash" />
                                    删除
                                </Button>
                            </div>
                        </div>
                        
                        <Divider />
                        
                        <div class="message-content">
                            <div class="content-text" v-html="formatContent(selectedMessage.content)"></div>
                            
                            <div v-if="selectedMessage.attachments && selectedMessage.attachments.length > 0" class="attachments">
                                <h4>附件</h4>
                                <div class="attachment-list">
                                    <div 
                                        v-for="attachment in selectedMessage.attachments" 
                                        :key="attachment.id"
                                        class="attachment-item">
                                        <Icon type="ios-document" />
                                        <span class="attachment-name">{{ attachment.name }}</span>
                                        <Button 
                                            type="text" 
                                            @click="downloadAttachment(attachment)"
                                            class="download-btn">
                                            <Icon type="ios-download" />
                                            下载
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div v-else class="empty-detail">
                        <Icon type="ios-mail-open" size="64" color="#ddd" />
                        <h3>选择消息查看详情</h3>
                        <p>从左侧列表中选择一条消息来查看其详细内容</p>
                    </div>
                </Card>
            </Col>
        </Row>

        <!-- 转发消息模态框 -->
        <Modal v-model="showForwardModal" title="转发消息" width="500">
            <Form :model="forwardForm" :label-width="80">
                <FormItem label="转发给">
                    <Select 
                        v-model="forwardForm.recipients" 
                        multiple 
                        placeholder="选择接收者"
                        class="forward-select">
                        <Option 
                            v-for="student in students" 
                            :key="student.id" 
                            :value="student.id">
                            {{ student.name }} ({{ student.gradeName }})
                        </Option>
                    </Select>
                </FormItem>
                <FormItem label="附加说明">
                    <Input 
                        v-model="forwardForm.note" 
                        type="textarea" 
                        :rows="3"
                        placeholder="可选：添加转发说明" />
                </FormItem>
            </Form>
            <template #footer>
                <Button @click="showForwardModal = false">取消</Button>
                <Button type="primary" @click="confirmForward" :loading="forwarding">
                    确认转发
                </Button>
            </template>
        </Modal>
    </div>
</template>

<script>
import { getUserMessages, markUserMessageRead, markAllUserMessagesRead, deleteUserMessage } from '@/api/index.js'
import { triggerBlobDownload } from '@/utils/fileDownload'

export default {
    name: 'MessageCenter',
    data() {
        return {
            loading: false,
            messages: [],
            filteredMessages: [],
            selectedMessage: null,
            filterType: '',
            showForwardModal: false,
            forwarding: false,
            forwardForm: {
                recipients: [],
                note: ''
            },
            students: [
                { id: 1, name: '张三', gradeName: '高三一班' },
                { id: 2, name: '李四', gradeName: '高三一班' },
                { id: 3, name: '王五', gradeName: '高三二班' }
            ]
        };
    },
    computed: {
        totalMessages() {
            return this.messages.length;
        },
        unreadCount() {
            return this.messages.filter(message => !message.isRead).length;
        },
        todayMessages() {
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            return this.messages.filter(message => {
                const messageDate = message.sendTime ? message.sendTime.split(' ')[0] : '';
                return messageDate === todayStr;
            }).length;
        }
    },
    methods: {
        async loadMessages() {
            try {
                this.loading = true;
                const token = this.$store.state.token || sessionStorage.getItem('token');

                if (!token) {
                    this.$Message.error('登录已过期，请重新登录');
                    this.$router.push('/login');
                    return;
                }

                const response = await getUserMessages(token, this.filterType);
                if (response.code === 0) {
                    const list = response.data || [];
                    // 兼容旧字段，统一 sender 字段用于展示
                    this.messages = list.map(m => ({
                        ...m,
                        sender: m.senderName || m.sender || ''
                    }));
                    this.filterMessages();
                } else if (response.code === 401 || response.code === 403) {
                    this.$Message.error('登录已过期，请重新登录');
                    this.$router.push('/login');
                } else {
                    this.$Message.error(response.msg || '加载消息失败');
                }
            } catch (error) {
                console.error('加载消息失败:', error);
                this.$Message.error('加载消息失败');
            } finally {
                this.loading = false;
            }
        },
        filterMessages() {
            if (!this.filterType) {
                this.filteredMessages = [...this.messages];
            } else {
                this.filteredMessages = this.messages.filter(message => 
                    message.type === this.filterType
                );
            }
        },
        selectMessage(message) {
            this.selectedMessage = message;
            // 标记消息为已读
            if (!message.isRead) {
                this.markAsRead(message.id);
            }
        },
        async markAsRead(messageId) {
            try {
                const token = this.$store.state.token || sessionStorage.getItem('token');
                await markUserMessageRead(token, messageId);
                // 本地更新
                const message = this.messages.find(m => m.id === messageId);
                if (message) {
                    message.isRead = true;
                }
                
                this.$Message.success('消息已标记为已读');
            } catch (error) {
                console.error('标记已读失败:', error);
                this.$Message.error('标记已读失败');
            }
        },
        async markAllAsRead() {
            try {
                const token = this.$store.state.token || sessionStorage.getItem('token');
                await markAllUserMessagesRead(token);
                // 本地更新
                this.messages.forEach(message => {
                    message.isRead = true;
                });
                
                this.$Message.success('所有消息已标记为已读');
            } catch (error) {
                console.error('标记全部已读失败:', error);
                this.$Message.error('标记全部已读失败');
            }
        },
        deleteMessage(messageId) {
            this.$Modal.confirm({
                title: '确认删除',
                content: '确定要删除这条消息吗？删除后无法恢复。',
                onOk: async () => {
                    try {
                        const token = this.$store.state.token || sessionStorage.getItem('token');
                        await deleteUserMessage(token, messageId);
                        // 本地更新
                        this.messages = this.messages.filter(m => m.id !== messageId);
                        this.filteredMessages = this.filteredMessages.filter(m => m.id !== messageId);
                        
                        if (this.selectedMessage && this.selectedMessage.id === messageId) {
                            this.selectedMessage = null;
                        }
                        
                        this.$Message.success('消息删除成功');
                    } catch (error) {
                        console.error('删除消息失败:', error);
                        this.$Message.error('删除消息失败');
                    }
                }
            });
        },
        forwardMessage(message) {
            this.selectedMessage = message;
            this.forwardForm.recipients = [];
            this.forwardForm.note = '';
            this.showForwardModal = true;
            // 加载学生列表用于转发
            this.loadStudents();
        },
        async loadStudents() {
            try {
                const { default: http } = await import('@/utils/http.js');
                const { getPageStudents } = await import('@/api/index.js');
                const response = await getPageStudents(1, 500, '', '', '');
                if (response.code === 0 && response.data && response.data.list) {
                    this.students = response.data.list.map(student => ({
                        id: student.id,
                        name: student.name,
                        gradeName: student.gradeName || ''
                    }));
                }
            } catch (error) {
                console.error('加载学生列表失败:', error);
                // 如果API失败，使用模拟数据
                this.students = [
                    { id: 1, name: '张三', gradeName: '高三一班' },
                    { id: 2, name: '李四', gradeName: '高三一班' },
                    { id: 3, name: '王五', gradeName: '高三二班' }
                ];
            }
        },
        async confirmForward() {
            if (this.forwardForm.recipients.length === 0) {
                this.$Message.warning('请选择接收者')
                return
            }
            
            if (!this.selectedMessage) {
                this.$Message.warning('请选择要转发的消息')
                return
            }
            
            this.forwarding = true
            try {
                const { default: http } = await import('@/utils/http.js');
                const token = this.$store.state.token || sessionStorage.getItem('token');
                
                // 构建表单数据
                const formData = new FormData();
                formData.append('token', token);
                formData.append('action', 'forward');
                formData.append('messageId', this.selectedMessage.id);
                this.forwardForm.recipients.forEach(recipientId => {
                    formData.append('recipientIds[]', recipientId);
                });
                if (this.forwardForm.note) {
                    formData.append('note', this.forwardForm.note);
                }
                
                const response = await http.post('/admin/messages/', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                
                if (response.code === 0) {
                    this.$Message.success('消息转发成功');
                    this.showForwardModal = false;
                    this.forwardForm.recipients = [];
                    this.forwardForm.note = '';
                    // 重新加载消息列表
                    this.loadMessages();
                } else {
                    this.$Message.error(response.msg || '消息转发失败');
                }
            } catch (error) {
                console.error('转发消息失败:', error);
                this.$Message.error('转发消息失败，请稍后重试');
            } finally {
                this.forwarding = false;
            }
        },
        async downloadAttachment(attachment) {
            try {
                // 验证附件对象
                if (!attachment || !attachment.id) {
                    this.$Message.error('附件信息无效')
                    return
                }

                // 检查文件大小（限制50MB）
                if (attachment.fileSize && attachment.fileSize > 50 * 1024 * 1024) {
                    this.$Message.warning('附件文件过大（超过50MB），无法下载')
                    return
                }

                // 若后端已返回可访问URL，直接打开
                if (attachment.url) {
                    window.open(attachment.url, '_blank');
                    return;
                }
                const { downloadMessageAttachment } = await import('@/api/index.js');
                const res = await downloadMessageAttachment(attachment.id);

                // 检查响应状态
                if (res.code !== undefined && res.code !== 0) {
                    this.$Message.error(res.msg || '下载附件失败，可能没有权限')
                    return
                }

                const blob = res.data || res; // 拦截器对blob返回原始响应
                triggerBlobDownload(blob, attachment.name || '附件')
            } catch (error) {
                console.error('下载附件失败:', error);
                this.$Message.error('下载附件失败，请稍后重试');
            }
        },
        getMessageTypeTag(type) {
            const tagTypeMap = {
                'notice': 'primary',
                'exam': 'success',
                'task': 'warning',
                'system': 'default'
            };
            return tagTypeMap[type] || 'default';
        },
        getMessageTypeText(type) {
            const typeTextMap = {
                'notice': '通知公告',
                'exam': '考试相关',
                'task': '任务通知',
                'system': '系统消息'
            };
            return typeTextMap[type] || '其他';
        },
        formatTime(timeStr) {
            if (!timeStr) return '';
            
            const date = new Date(timeStr);
            const now = new Date();
            const diff = now - date;
            
            // 小于1分钟
            if (diff < 60000) {
                return '刚刚';
            }
            // 小于1小时
            if (diff < 3600000) {
                return `${Math.floor(diff / 60000)}分钟前`;
            }
            // 小于24小时
            if (diff < 86400000) {
                return `${Math.floor(diff / 3600000)}小时前`;
            }
            // 小于7天
            if (diff < 604800000) {
                return `${Math.floor(diff / 86400000)}天前`;
            }
            // 超过7天显示具体日期
            return date.toLocaleDateString('zh-CN', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        formatContent(content) {
            // 简单的HTML内容格式化
            return content.replace(/\n/g, '<br>')
        },
        getPriorityColor(priority) {
            const colorMap = {
                'high': '#ff4757',
                'medium': '#ffa502',
                'low': '#2ed573'
            };
            return colorMap[priority] || '#2ed573';
        }
    },
    mounted() {
        this.loadMessages();
    }
};
</script>

<style scoped>
.fater-body-show {
    padding: 20px;
    background: #f5f7fa;
    min-height: 100vh;
}

.page-header {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content {
    display: flex;
    align-items: center;
}

.header-icon {
    font-size: 48px;
    margin-right: 20px;
    opacity: 0.9;
}

.header-text h2 {
    margin: 0 0 8px 0;
    font-size: 28px;
    font-weight: 600;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
}

.header-stats {
    display: flex;
    gap: 30px;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 14px;
    opacity: 0.8;
}

.message-container {
    margin-bottom: 24px;
}

.message-list-card,
.message-detail-card {
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    height: calc(100vh - 200px);
    overflow: hidden;
}

.card-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 18px;
    font-weight: 600;
}

.title-icon {
    margin-right: 10px;
    color: #1890ff;
}

.title-actions {
    display: flex;
    gap: 10px;
}

.action-btn {
    padding: 4px 8px;
    font-size: 12px;
}

.message-filters {
    margin-bottom: 20px;
}

.filter-select {
    width: 100%;
}

.message-list {
    height: calc(100vh - 350px);
    overflow-y: auto;
}

.message-item {
    padding: 15px;
    border-bottom: 1px solid #e8eaed;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 8px;
    margin-bottom: 8px;
}

.message-item:hover {
    background: #f8f9fa;
    transform: translateX(5px);
}

.message-item.selected {
    background: #e3f2fd;
    border-left: 3px solid #1890ff;
}

.message-item.unread {
    background: #fff3e0;
    border-left: 3px solid #ff9800;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.message-type {
    display: flex;
    gap: 5px;
}

.message-time {
    font-size: 12px;
    color: #7f8c8d;
}

.message-title {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
    line-height: 1.4;
}

.message-preview {
    font-size: 13px;
    color: #7f8c8d;
    line-height: 1.4;
    margin-bottom: 8px;
}

.message-status {
    display: flex;
    justify-content: flex-end;
    align-items: center;
}

.read-indicator {
    font-size: 12px;
    color: #7f8c8d;
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #7f8c8d;
}

.empty-state p {
    margin-top: 10px;
}

.message-detail {
    height: calc(100vh - 300px);
    overflow-y: auto;
}

.detail-header {
    margin-bottom: 20px;
}

.message-title-large {
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 15px;
    line-height: 1.3;
}

.message-info {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 15px;
}

.message-info span {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #7f8c8d;
    font-size: 14px;
}

.message-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.message-content {
    line-height: 1.8;
}

.content-text {
    color: #2c3e50;
    margin-bottom: 20px;
}

.attachments h4 {
    color: #1890ff;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e8eaed;
}

.attachment-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.attachment-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
}

.attachment-name {
    flex: 1;
    color: #2c3e50;
}

.download-btn {
    padding: 4px 8px;
    font-size: 12px;
}

.empty-detail {
    text-align: center;
    padding: 60px 20px;
    color: #7f8c8d;
}

.empty-detail h3 {
    margin: 20px 0 10px 0;
    color: #2c3e50;
}

.empty-detail p {
    margin: 0;
    line-height: 1.6;
}

.forward-select {
    width: 100%;
}

/* 动画效果 */
.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

.animate-fade-in-up.delay-100 {
    animation-delay: 0.1s;
}

.animate-fade-in-up.delay-200 {
    animation-delay: 0.2s;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }
    
    .header-stats {
        gap: 20px;
    }
    
    .message-container {
        flex-direction: column;
    }
    
    .message-list-card,
    .message-detail-card {
        height: auto;
        margin-bottom: 20px;
    }
    
    .message-list {
        height: 400px;
    }
    
    .message-detail {
        height: auto;
    }
    
    .message-info {
        flex-direction: column;
        gap: 10px;
    }
}
</style>
