<template>
    <div class="fater-body-show">
        <div class="page-header animate-fade-in-up">
            <div class="header-content">
                <Icon type="ios-pulse" class="header-icon" />
                <div class="header-text">
                    <h2>个人动态</h2>
                    <p>记录您的学习轨迹和成长历程</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ totalActivities }}</div>
                    <div class="stat-label">总活动数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ thisWeekActivities }}</div>
                    <div class="stat-label">本周活动</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ thisMonthActivities }}</div>
                    <div class="stat-label">本月活动</div>
                </div>
            </div>
        </div>

        <!-- 学习轨迹小结与趋势 -->
        <div class="overview-section animate-fade-in-up delay-100" v-if="trendDays.length || Object.keys(projectHeatMap).length">
            <Card class="overview-card">
                <template #title>
                    <div class="card-title">
                        <Icon type="ios-trending-up" class="title-icon" />
                        <span>最近学习趋势（7天）</span>
                    </div>
                </template>
                <div v-if="trendDays.length" class="mini-chart">
                    <div 
                        v-for="day in trendDays" 
                        :key="day.date"
                        class="mini-bar-wrapper"
                    >
                        <div class="mini-bar" :style="{ height: getDayBarHeight(day.count) }"></div>
                        <div class="mini-bar-label">{{ day.label }}</div>
                    </div>
                </div>
                <div v-else class="mini-chart-empty">近期暂无学习活动</div>
            </Card>

            <Card class="overview-card">
                <template #title>
                    <div class="card-title">
                        <Icon type="ios-flame" class="title-icon" />
                        <span>按科目学习热度</span>
                    </div>
                </template>
                <div v-if="Object.keys(projectHeatMap).length" class="mini-chart">
                    <div 
                        v-for="(count, project) in projectHeatMap" 
                        :key="project"
                        class="mini-bar-wrapper"
                    >
                        <div class="mini-bar subject" :style="{ height: getProjectBarHeight(count) }"></div>
                        <div class="mini-bar-label">{{ project }}</div>
                    </div>
                </div>
                <div v-else class="mini-chart-empty">暂无按科目统计数据</div>
            </Card>
        </div>

        <Card class="filter-card animate-fade-in-up delay-100">
            <template #title>
                <div class="card-title">
                    <Icon type="ios-funnel" class="title-icon" />
                    <span>动态筛选</span>
                </div>
            </template>
            <div class="filter-form">
                <Form :model="filterForm" inline class="modern-form">
                    <FormItem class="form-item">
                        <Select 
                            v-model="filterForm.activityType" 
                            placeholder="活动类型"
                            class="modern-select">
                            <Option value="">全部类型</Option>
                            <Option value="exam">考试</Option>
                            <Option value="practice">练习</Option>
                            <Option value="task">任务</Option>
                            <Option value="login">登录</Option>
                            <Option value="profile">资料更新</Option>
                        </Select>
                    </FormItem>
                    <FormItem class="form-item">
                        <DatePicker 
                            v-model="filterForm.dateRange" 
                            type="daterange" 
                            placeholder="选择日期范围"
                            class="modern-date-picker">
                        </DatePicker>
                    </FormItem>
                    <FormItem class="form-item">
                        <Button 
                            type="primary" 
                            @click="filterActivities()"
                            class="filter-btn btn-ripple">
                            <Icon type="ios-search" />
                            筛选
                        </Button>
                        <Button 
                            @click="resetFilter()"
                            class="reset-btn btn-ripple">
                            <Icon type="ios-refresh" />
                            重置
                        </Button>
                    </FormItem>
                </Form>
            </div>
        </Card>

        <div class="timeline-container animate-fade-in-up delay-200">
            <Timeline>
                <TimelineItem 
                    v-for="activity in filteredActivities" 
                    :key="activity.id"
                    :color="getActivityColor(activity.type)"
                    :icon="getActivityIcon(activity.type)">
                    <div class="timeline-content">
                        <div class="activity-header">
                            <div class="activity-title">
                                <Icon :type="getActivityIcon(activity.type)" class="activity-icon" />
                                <span class="title-text">{{ activity.title }}</span>
                                <Tag :type="getActivityTagType(activity.type)" class="type-tag">
                                    {{ getActivityTypeText(activity.type) }}
                                </Tag>
                            </div>
                            <div class="activity-time">
                                <Icon type="ios-time-outline" />
                                <span>{{ formatTime(activity.createTime) }}</span>
                            </div>
                        </div>
                        <div class="activity-content">
                            <p class="activity-description">{{ activity.description }}</p>
                            <div v-if="activity.details" class="activity-details">
                                <div v-for="(detail, key) in activity.details" :key="key" class="detail-item">
                                    <span class="detail-label">{{ detail.label }}:</span>
                                    <span class="detail-value">{{ detail.value }}</span>
                                </div>
                            </div>
                        </div>
                        <div v-if="activity.actions" class="activity-actions">
                            <Button 
                                v-for="action in activity.actions" 
                                :key="action.key"
                                :type="action.type || 'default'"
                                size="small"
                                @click="handleAction(action, activity)"
                                class="action-btn">
                                <Icon :type="action.icon" />
                                {{ action.text }}
                            </Button>
                        </div>
                    </div>
                </TimelineItem>
            </Timeline>
        </div>

        <!-- 动态详情模态框 -->
        <Modal v-model="showDetailModal" title="动态详情" width="600">
            <div v-if="selectedActivity" class="activity-detail-modal">
                <div class="detail-section">
                    <h4>基本信息</h4>
                    <div class="detail-row">
                        <span class="label">活动类型:</span>
                        <span class="value">{{ getActivityTypeText(selectedActivity.type) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">发生时间:</span>
                        <span class="value">{{ formatTime(selectedActivity.createTime) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">活动描述:</span>
                        <span class="value">{{ selectedActivity.description }}</span>
                    </div>
                </div>
                
                <div v-if="selectedActivity.details" class="detail-section">
                    <h4>详细信息</h4>
                    <div v-for="(detail, key) in selectedActivity.details" :key="key" class="detail-row">
                        <span class="label">{{ detail.label }}:</span>
                        <span class="value">{{ detail.value }}</span>
                    </div>
                </div>

                <div v-if="selectedActivity.relatedData" class="detail-section">
                    <h4>相关数据</h4>
                    <div v-for="(data, key) in selectedActivity.relatedData" :key="key" class="detail-row">
                        <span class="label">{{ data.label }}:</span>
                        <span class="value">{{ data.value }}</span>
                    </div>
                </div>
            </div>
            <template #footer>
                <Button @click="showDetailModal = false">关闭</Button>
            </template>
        </Modal>
    </div>
</template>

<script>
import { getLoginUser } from '@/api/index.js'

export default {
    name: 'PersonalDynamics',
    data() {
        return {
            loading: false,
            activities: [],
            filteredActivities: [],
            totalActivities: 0,
            thisWeekActivities: 0,
            thisMonthActivities: 0,
            selectedActivity: null,
            showDetailModal: false,
            // 趋势与热度可视化数据
            trendDays: [],
            projectHeatMap: {},
            filterForm: {
                activityType: '',
                dateRange: []
            },
            // 模拟活动数据，实际项目中应该从API获取
            mockActivities: [
                {
                    id: 1,
                    type: 'exam',
                    title: '参加了《数据结构》期末考试',
                    description: '在2024年春季学期期末考试中取得了85分的成绩',
                    details: {
                        '考试科目': '数据结构',
                        '考试时间': '2024-06-15 14:00-16:00',
                        '考试成绩': '85分',
                        '考试状态': '已完成'
                    },
                    createTime: '2024-06-15 16:30:00'
                },
                {
                    id: 2,
                    type: 'practice',
                    title: '完成了《算法设计》练习题',
                    description: '成功完成了10道算法练习题，正确率80%',
                    details: {
                        '练习科目': '算法设计',
                        '题目数量': '10题',
                        '正确率': '80%',
                        '用时': '45分钟'
                    },
                    createTime: '2024-06-14 20:15:00'
                },
                {
                    id: 3,
                    type: 'task',
                    title: '提交了《软件工程》项目任务',
                    description: '按时完成了软件工程课程设计项目，获得优秀评价',
                    details: {
                        '任务名称': '在线考试系统设计',
                        '提交时间': '2024-06-13 23:59:00',
                        '任务状态': '已完成',
                        '评价等级': '优秀'
                    },
                    createTime: '2024-06-13 23:59:00'
                },
                {
                    id: 4,
                    type: 'login',
                    title: '系统登录',
                    description: '成功登录在线考试系统',
                    details: {
                        '登录时间': '2024-06-12 09:00:00',
                        '登录IP': '192.168.1.100',
                        '登录设备': 'Chrome浏览器'
                    },
                    createTime: '2024-06-12 09:00:00'
                },
                {
                    id: 5,
                    type: 'profile',
                    title: '更新个人信息',
                    description: '修改了个人头像和联系方式',
                    details: {
                        '更新项目': '头像、手机号',
                        '更新时间': '2024-06-11 15:30:00'
                    },
                    createTime: '2024-06-11 15:30:00'
                }
            ]
        };
    },
    computed: {
        // 保留computed属性作为备用，但主要数据由loadActivities方法设置
    },
    methods: {
        filterActivities() {
            let filtered = [...this.activities];
            
            // 按活动类型筛选
            if (this.filterForm.activityType) {
                filtered = filtered.filter(activity => activity.type === this.filterForm.activityType);
            }
            
            // 按日期范围筛选
            if (this.filterForm.dateRange && this.filterForm.dateRange.length === 2) {
                const startDate = new Date(this.filterForm.dateRange[0]);
                const endDate = new Date(this.filterForm.dateRange[1]);
                endDate.setHours(23, 59, 59, 999);
                
                filtered = filtered.filter(activity => {
                    const activityDate = new Date(activity.createTime);
                    return activityDate >= startDate && activityDate <= endDate;
                });
            }
            
            this.filteredActivities = filtered;
        },
        resetFilter() {
            this.filterForm.activityType = '';
            this.filterForm.dateRange = [];
            this.filteredActivities = [...this.activities];
        },
        getActivityColor(type) {
            const colorMap = {
                'exam': 'blue',
                'practice': 'green',
                'task': 'orange',
                'login': 'purple',
                'profile': 'cyan'
            };
            return colorMap[type] || 'blue';
        },
        getActivityIcon(type) {
            const iconMap = {
                'exam': 'ios-document',
                'practice': 'ios-book',
                'task': 'ios-list-box',
                'login': 'ios-log-in',
                'profile': 'ios-person'
            };
            return iconMap[type] || 'ios-information';
        },
        getActivityTagType(type) {
            const tagTypeMap = {
                'exam': 'primary',
                'practice': 'success',
                'task': 'warning',
                'login': 'default',
                'profile': 'info'
            };
            return tagTypeMap[type] || 'default';
        },
        getActivityTypeText(type) {
            const typeTextMap = {
                'exam': '考试',
                'practice': '练习',
                'task': '任务',
                'login': '登录',
                'profile': '资料'
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
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        handleAction(action, activity) {
            switch (action.key) {
                case 'view':
                    this.showActivityDetail(activity)
                    break
                case 'review':
                    this.reviewWrongQuestions(activity)
                    break
                default:
                    console.log('处理动作:', action.key, activity)
            }
        },
        showActivityDetail(activity) {
            this.selectedActivity = activity
            this.showDetailModal = true
        },
        reviewWrongQuestions(activity) {
            // 跳转到错题本页面
            this.$router.push({ name: 'wrongQuestions' });
        },
        async loadActivities() {
            try {
                this.loading = true;
                const token = this.$store.state.token || sessionStorage.getItem('token');
                const activities = [];
                
                // 导入API函数
                const { 
                    getPageStudentExamLogs, 
                    getPracticeLogs, 
                    getTaskLogs 
                } = await import('@/api/index.js');
                
                // 1. 获取考试记录
                try {
                    const examResponse = await getPageStudentExamLogs(1, 50, '', '', '');
                    if (examResponse.code === 0 && examResponse.data && examResponse.data.list) {
                        examResponse.data.list.forEach(log => {
                            activities.push({
                                id: `exam_${log.id}`,
                                type: 'exam',
                                title: `参加了考试：${log.examName || '未知考试'}`,
                                description: `得分：${log.score || 0}分，状态：${log.status === 2 ? '已完成' : '进行中'}`,
                                createTime: log.createTime || new Date().toISOString(),
                                details: {
                                    examName: log.examName,
                                    score: log.score,
                                    status: log.status,
                                    projectName: log.projectName
                                }
                            });
                        });
                    }
                } catch (error) {
                    console.error('加载考试记录失败:', error);
                }
                
                // 2. 获取练习记录
                try {
                    const practiceResponse = await getPracticeLogs(token);
                    if (practiceResponse.code === 0 && practiceResponse.data) {
                        practiceResponse.data.forEach(log => {
                            activities.push({
                                id: `practice_${log.id}`,
                                type: 'practice',
                                title: `完成了练习：${log.paperTitle || '未知练习'}`,
                                description: `得分：${log.score || 0}分，正确率：${(log.accuracy * 100).toFixed(1)}%，用时：${log.usedTime || 0}分钟`,
                                createTime: log.endTime || log.startTime || new Date().toISOString(),
                                details: {
                                    paperTitle: log.paperTitle,
                                    score: log.score,
                                    accuracy: log.accuracy,
                                    usedTime: log.usedTime,
                                    projectName: log.projectName
                                }
                            });
                        });
                    }
                } catch (error) {
                    console.error('加载练习记录失败:', error);
                }
                
                // 3. 获取任务记录
                try {
                    const taskResponse = await getTaskLogs(token);
                    if (taskResponse.code === 0 && taskResponse.data) {
                        taskResponse.data.forEach(log => {
                            activities.push({
                                id: `task_${log.id}`,
                                type: 'task',
                                title: `完成了任务：${log.taskTitle || '未知任务'}`,
                                description: `得分：${log.score || 0}分，正确率：${(log.accuracy * 100).toFixed(1)}%，用时：${log.usedTime || 0}分钟`,
                                createTime: log.endTime || log.startTime || new Date().toISOString(),
                                details: {
                                    taskTitle: log.taskTitle,
                                    score: log.score,
                                    accuracy: log.accuracy,
                                    usedTime: log.usedTime
                                }
                            });
                        });
                    }
                } catch (error) {
                    console.error('加载任务记录失败:', error);
                }
                
                // 按时间排序（最新的在前）
                activities.sort((a, b) => {
                    return new Date(b.createTime) - new Date(a.createTime);
                });
                
                this.activities = activities;
                this.filteredActivities = [...activities];
                
                // 计算统计数据与可视化数据
                this.calculateStatsAndTrends(activities);
                
            } catch (error) {
                console.error('加载个人动态失败:', error);
                this.$Message.error('加载个人动态失败');
            } finally {
                this.loading = false;
            }
        },

        calculateStatsAndTrends(activities) {
                this.totalActivities = activities.length;
                const now = new Date();
                const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                
                this.thisWeekActivities = activities.filter(a => {
                    const date = new Date(a.createTime);
                    return date >= weekAgo;
                }).length;
                
                this.thisMonthActivities = activities.filter(a => {
                    const date = new Date(a.createTime);
                    return date >= monthAgo;
                }).length;
                
            // 7天趋势：按日期统计活动数
            const dayMap = {};
            for (let i = 6; i >= 0; i--) {
                const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
                const key = d.toISOString().slice(0, 10);
                dayMap[key] = 0;
            }
            activities.forEach(a => {
                const key = new Date(a.createTime).toISOString().slice(0, 10);
                if (dayMap[key] !== undefined) {
                    dayMap[key] += 1;
                }
            });
            this.trendDays = Object.keys(dayMap).map(k => ({
                date: k,
                count: dayMap[k],
                label: k.slice(5).replace('-', '/')
            }));

            // 科目热度：仅对有 projectName 的活动统计
            const projectMap = {};
            activities.forEach(a => {
                const projectName = a.details && (a.details.projectName || a.details.subject || a.details.examName);
                if (projectName) {
                    projectMap[projectName] = (projectMap[projectName] || 0) + 1;
                }
            });
            this.projectHeatMap = projectMap;
        },

        getDayBarHeight(count) {
            const max = Math.max(...this.trendDays.map(d => d.count), 1);
            const pct = Math.round((count / max) * 80) + 10; // 10%~90%
            return `${pct}%`;
        },

        getProjectBarHeight(count) {
            const values = Object.values(this.projectHeatMap);
            const max = Math.max(...values, 1);
            const pct = Math.round((count / max) * 80) + 10;
            return `${pct}%`;
        }
    },
    mounted() {
        this.loadActivities();
    }
};
</script>

<style scoped>
.fater-body-show {
    padding: 24px;
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    min-height: 100vh;
    animation: fadeInUp 0.6s ease-out;
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

.page-header {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(24, 144, 255, 0.3);
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
    color: #fff;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 16px;
    color: rgba(255, 255, 255, 0.9);
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
    color: #fff;
}

.stat-label {
    font-size: 14px;
    opacity: 0.8;
    color: rgba(255, 255, 255, 0.9);
}

.filter-card {
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    background: #fff;
    transition: all 0.3s ease;
}

.filter-card:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
}

.overview-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}

.overview-card {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    background: #fff;
    transition: all 0.3s ease;
}

.overview-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.2);
}

.mini-chart {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding: 16px 10px 10px;
    height: 140px;
}

.mini-chart-empty {
    padding: 20px;
    text-align: center;
    color: #8c8c8c;
    font-size: 13px;
}

.mini-bar-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
}

.mini-bar {
    width: 12px;
    border-radius: 6px 6px 0 0;
    background: linear-gradient(180deg, #1890ff, #0050b3);
    transition: height 0.3s ease;
}

.mini-bar.subject {
    background: linear-gradient(180deg, #52c41a, #389e0d);
}

.mini-bar-label {
    margin-top: 6px;
    font-size: 11px;
    color: #595959;
    white-space: nowrap;
}

.card-title {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
    color: #262626;
}

.title-icon {
    margin-right: 10px;
    color: #1890ff;
}

.filter-form {
    padding: 20px 0;
}

.modern-form {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
}

.form-item {
    margin-bottom: 0;
}

.modern-select,
.modern-date-picker {
    min-width: 150px;
}

.filter-btn,
.reset-btn {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
}

.timeline-container {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
    transition: all 0.3s ease;
}

.timeline-container:hover {
    box-shadow: 0 8px 30px rgba(24, 144, 255, 0.15);
}

.timeline-content {
    padding: 20px;
    background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
    border-radius: 10px;
    margin-left: 20px;
    border-left: 3px solid #1890ff;
    transition: all 0.3s ease;
}

.timeline-content:hover {
    background: linear-gradient(135deg, #e6f7ff 0%, #fff 100%);
    transform: translateX(4px);
}

.activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.activity-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.activity-icon {
    font-size: 20px;
    color: #1890ff;
}

.title-text {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
}

.type-tag {
    font-size: 12px;
}

.activity-time {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #8c8c8c;
    font-size: 14px;
}

.activity-content {
    margin-bottom: 15px;
}

.activity-description {
    margin: 0 0 10px 0;
    color: #595959;
    line-height: 1.6;
}

.activity-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.detail-item {
    display: flex;
    gap: 8px;
}

.detail-label {
    font-weight: 600;
    color: #8c8c8c;
    min-width: 80px;
}

.detail-value {
    color: #262626;
}

.activity-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.action-btn {
    border-radius: 6px;
    font-size: 12px;
}

.action-btn.ivu-btn-primary {
    background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
    border: none;
    transition: all 0.3s ease;
}

.action-btn.ivu-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .fater-body-show {
        padding: 16px;
    }

    .page-header {
        flex-direction: column;
        gap: 16px;
        padding: 20px;
    }

    .header-text h2 {
        font-size: 22px;
    }

    .header-stats {
        flex-wrap: wrap;
        gap: 16px;
    }

    .overview-section {
        grid-template-columns: 1fr;
    }
}

.activity-detail-modal {
    padding: 20px 0;
}

.detail-section {
    margin-bottom: 25px;
}

.detail-section h4 {
    color: #667eea;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e8eaed;
}

.detail-row {
    display: flex;
    margin-bottom: 10px;
    padding: 8px 0;
}

.detail-row .label {
    font-weight: 600;
    color: #7f8c8d;
    min-width: 100px;
}

.detail-row .value {
    color: #2c3e50;
    flex: 1;
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
    
    .modern-form {
        flex-direction: column;
        align-items: stretch;
    }
    
    .form-item {
        width: 100%;
    }
    
    .activity-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .activity-details {
        grid-template-columns: 1fr;
    }
}
</style>
