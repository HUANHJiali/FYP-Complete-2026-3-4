<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-list-box" class="header-icon" />
                <div class="header-text">
                    <h2>任务中心</h2>
                    <p>完成管理员发布的年级任务，每个学生只能做一次</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalTasks }}</div>
                    <div class="stat-label">总任务数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ inProgressTasks }}</div>
                    <div class="stat-label">进行中</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ completedTasks }}</div>
                    <div class="stat-label">已完成</div>
                </div>
                <div class="stat-item" :class="{ 'warning': overdueTasks > 0 }">
                    <div class="stat-number">{{ overdueTasks }}</div>
                    <div class="stat-label">已逾期</div>
                </div>
            </div>
        </div>

        <Card class="filter-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-search" class="title-icon" />
                    <span>任务筛选</span>
                </div>
            </template>
            <div class="filter-form">
                <Form :model="filterForm" inline class="modern-form">
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.status" 
                            placeholder="任务状态"
                            class="modern-select">
                            <Option value="">全部状态</Option>
                            <Option value="not_started">未开始</Option>
                            <Option value="in_progress">进行中</Option>
                            <Option value="completed">已完成</Option>
                            <Option value="overdue">已逾期</Option>
                        </Select>
                    </FormItem>
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.projectId" 
                            placeholder="选择科目"
                            class="modern-select">
                            <Option value="">全部科目</Option>
                            <Option v-for="project in projects" 
                                :key="project.id" 
                                :value="String(project.id)" :label="String(project.name)">{{ project.name }}</Option>
                        </Select>
                    </FormItem>
                    <FormItem class="form-item">
                        <Button 
                            type="primary" 
                            @click="filterTasks()"
                            class="filter-btn btn-ripple">
                            <Icon type="ios-search" />
                            筛选
                        </Button>
                    </FormItem>
                </Form>
            </div>
        </Card>

        <div class="tasks-grid animate-fade-in-up delay-200">
            <Card 
                v-for="task in filteredTasks" 
                :key="task.id" 
                class="task-card"
                :class="{ 'completed': getTaskLifecycle(task) === 'completed' }">
                <template #title>
                    <div class="task-header">
                        <div class="task-title">
                            <Icon :type="getTaskIcon(task.type)" class="task-icon" />
                            <span>{{ task.title }}</span>
                            <Tag 
                                :type="getStatusType(getTaskLifecycle(task))" 
                                class="status-tag">
                                {{ getStatusText(getTaskLifecycle(task)) }}
                            </Tag>
                        </div>
                        <div class="task-meta">
                            <span class="deadline" :class="getDeadlineClass(task)">
                                <Icon type="ios-time" />
                                {{ formatDeadline(task.deadline) }}
                                <span v-if="getDeadlineBadge(task)" class="deadline-badge">
                                    {{ getDeadlineBadge(task) }}
                                </span>
                            </span>
                        </div>
                    </div>
                </template>
                
                <div class="task-content">
                    <p class="task-description">{{ task.description }}</p>
                    
                    <div class="task-info">
                        <div class="info-item">
                            <Icon type="ios-ribbon" />
                            <span>科目：{{ task.projectName }}</span>
                        </div>
                        <div class="info-item">
                            <Icon type="ios-people" />
                            <span>年级：{{ task.gradeName }}</span>
                        </div>
                        <div class="info-item">
                            <Icon type="ios-star" />
                            <span>分值：{{ task.score }}分</span>
                        </div>
                        <div v-if="getTaskLifecycle(task) === 'completed'" class="info-item">
                            <Icon type="ios-trophy" />
                            <span>得分：{{ task.score }}分</span>
                        </div>
                        <div v-if="getTaskLifecycle(task) === 'completed'" class="info-item">
                            <Icon type="ios-checkmark-circle" />
                            <span>正确率：{{ task.accuracy }}%</span>
                        </div>
                    </div>

                    <div class="task-progress">
                        <Progress :percent="getTaskProgress(task)" :status="getProgressStatus(task)" />
                    </div>

                    <div class="task-actions">
                        <Button 
                            v-if="getTaskLifecycle(task) === 'not_started'"
                            type="primary" 
                            @click="startTask(task)"
                            :disabled="isTaskOverdue(task)"
                            class="start-btn btn-ripple">
                            <Icon type="ios-play" />
                            {{ isTaskOverdue(task) ? '任务已逾期' : '开始任务' }}
                        </Button>
                        <Button 
                            v-else-if="getTaskLifecycle(task) === 'in_progress'"
                            type="warning" 
                            @click="continueTask(task)"
                            :disabled="isTaskOverdue(task)"
                            class="continue-btn btn-ripple">
                            <Icon type="ios-play" />
                            {{ isTaskOverdue(task) ? '任务已逾期' : '继续任务' }}
                        </Button>
                        <Button 
                            v-else-if="getTaskLifecycle(task) === 'completed'"
                            type="success" 
                            @click="viewResult(task)"
                            class="view-btn btn-ripple">
                            <Icon type="ios-eye" />
                            查看结果
                        </Button>
                        <Button 
                            @click="showTaskDetail(task)"
                            class="detail-btn btn-ripple">
                            <Icon type="ios-information" />
                            任务详情
                        </Button>
                    </div>
                </div>
            </Card>
        </div>

        <!-- 任务详情模态框 -->
        <Modal v-model="showDetailModal" title="任务详情" width="600">
            <div v-if="selectedTask" class="task-detail">
                <h3>{{ selectedTask.title }}</h3>
                <p class="detail-description">{{ selectedTask.description }}</p>
                
                <Divider>任务要求</Divider>
                <div class="requirements">
                    <p><strong>完成时间：</strong>{{ selectedTask.deadline }}</p>
                    <p><strong>任务分值：</strong>{{ selectedTask.score }}分</p>
                    <p><strong>任务类型：</strong>{{ getTaskTypeText(selectedTask.type) }}</p>
                    <p><strong>发布教师：</strong>{{ selectedTask.teacherName }}</p>
                </div>

                <Divider>注意事项</Divider>
                <ul class="notes">
                    <li>每个学生只能完成一次该任务</li>
                    <li>请在规定时间内完成任务</li>
                    <li>完成后将自动进入审核流程</li>
                </ul>
            </div>
        </Modal>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
            <Spin size="large">
                <Icon type="ios-loading" class="spin-icon-load"></Icon>
                <div class="spin-text">加载中...</div>
            </Spin>
        </div>
    </div>
</template>

<style scoped>
.page-header {
    margin-bottom: 24px;
    padding: 24px;
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border-radius: 12px;
    color: #000;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.header-icon {
    font-size: 32px;
    color: #000;
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
    gap: 24px;
}

.stat-item {
    text-align: center;
    background: rgba(255, 255, 255, 0.1);
    padding: 16px 24px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.stat-item.warning {
    background: rgba(255, 77, 79, 0.2);
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    opacity: 0.9;
}

.filter-card {
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
}

.title-icon {
    color: #1890ff;
}

.filter-form {
    padding: 20px 0;
}

.modern-form {
    display: flex;
    align-items: center;
    gap: 16px;
}

.form-item {
    margin-bottom: 0;
}

.modern-select {
    width: 200px;
}

.filter-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    height: 36px;
    padding: 0 20px;
    border-radius: 8px;
}

.tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 24px;
}

.task-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.task-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.task-card.completed {
    border-color: #52c41a;
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.task-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    flex: 1;
}

.task-icon {
    color: #1890ff;
    font-size: 18px;
}

.status-tag {
    margin-left: auto;
}

.task-meta {
    font-size: 12px;
    color: #8c8c8c;
}

.deadline {
    display: flex;
    align-items: center;
    gap: 4px;
}

.deadline.overdue {
    color: #ff4d4f;
}

.deadline.soon {
    color: #faad14;
}

.deadline-badge {
    margin-left: 8px;
    padding: 0 6px;
    border-radius: 10px;
    font-size: 12px;
    background: rgba(255, 255, 255, 0.2);
}

.task-content {
    padding: 16px 0;
}

.task-description {
    color: #595959;
    line-height: 1.6;
    margin-bottom: 16px;
}

.task-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #8c8c8c;
    font-size: 14px;
}

.task-actions {
    display: flex;
    gap: 12px;
}

.task-progress {
    margin: 12px 0 8px;
}

.start-btn,
.view-btn,
.detail-btn {
    height: 36px;
    padding: 0 16px;
    border-radius: 8px;
    font-size: 14px;
}

.start-btn {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
}

.view-btn {
    background: #52c41a;
    border: none;
}

.continue-btn {
    background: #faad14;
    border: none;
}

.detail-btn {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #6c757d;
}

.btn-ripple {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.btn-ripple:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.task-detail h3 {
    color: #262626;
    margin-bottom: 16px;
}

.detail-description {
    color: #595959;
    line-height: 1.6;
    margin-bottom: 20px;
}

.requirements p {
    margin-bottom: 8px;
    color: #595959;
}

.notes {
    color: #595959;
    line-height: 1.6;
}

.notes li {
    margin-bottom: 8px;
}

/* 加载状态样式 */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.spin-icon-load {
    animation: spin-rotate 1s infinite linear;
}

.spin-text {
    margin-top: 8px;
    color: #666;
}

@keyframes spin-rotate {
    100% {
        transform: rotate(360deg);
    }
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
</style>

<script>
import { getAllProjects, getStudentTasks, startTask } from '../../api/index.js';
import { normalizeLifecycleStatus, getLifecycleTagType, getLifecycleText } from '../../utils/lifecycleStatus';

export default {
    name: 'TaskCenter',
    data() {
        return {
            loading: false,
            filterForm: {
                status: '',
                projectId: ''
            },
            projects: [],
            tasks: [],
            showDetailModal: false,
            selectedTask: null
        };
    },
    computed: {
        filteredTasks() {
            let filtered = this.tasks;
            
            if (this.filterForm.status) {
                filtered = filtered.filter(task => this.getTaskLifecycle(task) === this.filterForm.status);
            }
            
            if (this.filterForm.projectId) {
                filtered = filtered.filter(task => task.projectId == this.filterForm.projectId);
            }
            
            return filtered;
        },
        completedTasks() {
            return this.tasks.filter(task => this.getTaskLifecycle(task) === 'completed').length;
        },
        totalTasks() {
            return this.tasks.length;
        },
        inProgressTasks() {
            return this.tasks.filter(task => this.getTaskLifecycle(task) === 'in_progress').length;
        },
        overdueTasks() {
            return this.tasks.filter(task => this.getTaskLifecycle(task) === 'overdue').length;
        }
    },
    methods: {
        getTaskLifecycle(task) {
            return normalizeLifecycleStatus(task);
        },
        // 加载任务列表
        loadTasks() {
            this.loading = true;
            const token = this.$store.state.token || sessionStorage.getItem('token');
            
            getStudentTasks(token).then(resp => {
                if (resp.code === 0) {
                    this.tasks = resp.data;
                } else {
                    this.$Message.error(resp.msg || '加载任务失败');
                }
            }).catch(error => {
                console.error('加载任务失败:', error);
                this.$Message.error('加载任务失败，请检查网络连接');
            }).finally(() => {
                this.loading = false;
            });
        },
        
        filterTasks() {
            // 筛选任务逻辑
            console.log('筛选条件：', this.filterForm);
        },
        
        // 开始任务
        startTask(task) {
            if (this.isTaskOverdue(task)) {
                this.$Message.warning('任务已截止，不能开始');
                return;
            }
            const token = this.$store.state.token || sessionStorage.getItem('token');
            
            startTask(token, task.id).then(resp => {
                if (resp.code === 0) {
                    this.$Message.success('任务开始成功！');
                    // 跳转到答题页面
                    this.$router.push({
                        name: 'answer',
                        query: {
                            type: 'task',
                            taskId: task.id,
                            logId: resp.data.logId
                        }
                    });
                } else {
                    this.$Message.error(resp.msg || '开始任务失败');
                }
            }).catch(error => {
                console.error('开始任务失败:', error);
                this.$Message.error('开始任务失败，请检查网络连接');
            });
        },
        
        // 继续任务
        continueTask(task) {
            if (this.isTaskOverdue(task)) {
                this.$Message.warning('任务已截止，不能继续作答');
                return;
            }
            this.$Message.info(`继续任务：${task.title}`);
            // 跳转到答题页面，继续现有任务
            this.$router.push({
                name: 'answer',
                query: {
                    type: 'task',
                    taskId: task.id,
                    logId: task.logId
                }
            });
        },
        
        async viewResult(task) {
            if (!task.logId) {
                this.$Message.warning('该任务尚未完成，无法查看结果');
                return;
            }
            
            try {
                const { getTaskLogInfo, getTaskAnswers } = await import('@/api/index.js');
                
                // 获取任务日志详细信息
                const logResponse = await getTaskLogInfo(task.logId);
                if (logResponse.code !== 0) {
                    this.$Message.error(logResponse.msg || '获取任务结果失败');
                    return;
                }
                
                // 获取任务答题记录
                const answersResponse = await getTaskAnswers(task.logId);
                if (answersResponse.code !== 0) {
                    this.$Message.error(answersResponse.msg || '获取答题记录失败');
                    return;
                }
                
                // 显示任务结果详情
                this.selectedTask = {
                    ...task,
                    logInfo: logResponse.data,
                    answers: answersResponse.data || []
                };
                this.showDetailModal = true;
            } catch (error) {
                console.error('获取任务结果失败:', error);
                this.$Message.error('获取任务结果失败，请稍后重试');
            }
        },
        
        showTaskDetail(task) {
            this.selectedTask = task;
            this.showDetailModal = true;
        },
        
        getTaskIcon(type) {
            const icons = {
                'practice': 'ios-book',
                'exam': 'ios-document',
                'project': 'ios-code'
            };
            return icons[type] || 'ios-list';
        },
        
        getStatusType(status) {
            return getLifecycleTagType(status);
        },
        
        getStatusText(status) {
            return getLifecycleText(status);
        },
        
        getTaskTypeText(type) {
            const texts = {
                'practice': '练习任务',
                'exam': '考试任务',
                'project': '项目任务'
            };
            return texts[type] || '普通任务';
        },

        formatDeadline(deadline) {
            if (!deadline) return '无截止时间';
            return deadline;
        },

        getDeadlineClass(task) {
            if (!task.deadline || this.getTaskLifecycle(task) === 'completed') return '';
            if (this.getTaskLifecycle(task) === 'overdue') return 'overdue';
            const now = new Date();
            const d = new Date(task.deadline);
            const diff = d.getTime() - now.getTime();
            const oneDay = 24 * 60 * 60 * 1000;
            if (diff < 0) return 'overdue';
            if (diff <= oneDay) return 'soon';
            return '';
        },

        getDeadlineBadge(task) {
            if (!task.deadline || this.getTaskLifecycle(task) === 'completed') return '';
            if (this.getTaskLifecycle(task) === 'overdue') return '已逾期';
            const now = new Date();
            const d = new Date(task.deadline);
            const diff = d.getTime() - now.getTime();
            const oneDay = 24 * 60 * 60 * 1000;
            if (diff < 0) return '已逾期';
            if (diff <= oneDay) return '即将到期';
            return '';
        },

        isTaskOverdue(task) {
            return this.getTaskLifecycle(task) === 'overdue';
        },

        getTaskProgress(task) {
            const lifecycle = this.getTaskLifecycle(task);
            if (lifecycle === 'completed') return 100;
            if (lifecycle === 'in_progress') return 60;
            if (lifecycle === 'overdue') return 20;
            return 10;
        },

        getProgressStatus(task) {
            if (task.status === 'completed') return 'success';
            if (this.getDeadlineClass(task) === 'overdue') return 'wrong';
            if (this.getDeadlineClass(task) === 'soon') return 'active';
            return 'normal';
        },
        
        loadProjects() {
            getAllProjects().then(resp => {
                if (resp.code === 0) {
                    this.projects = resp.data;
                }
            }).catch(error => {
                console.error('加载科目失败:', error);
            });
        }
    },
    mounted() {
        this.loadProjects();
        this.loadTasks();
    }
};
</script>
