<template>
    <div class="dashboard">
        <div class="dashboard-header">
            <h2>系统概览</h2>
            <p>实时监控系统运行状态</p>
        </div>
        
        <!-- 实时监控组件 -->
        <RealTimeMonitor />
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card" v-for="stat in stats" :key="stat.id">
                <div class="stat-icon" :style="{ background: stat.color }">
                    <Icon :type="stat.icon" />
                </div>
                <div class="stat-content">
                    <div class="stat-number">{{ stat.value }}</div>
                    <div class="stat-label">{{ stat.label }}</div>
                    <div class="stat-change" :class="stat.trend">
                        <Icon :type="stat.trend === 'up' ? 'ios-arrow-up' : 'ios-arrow-down'" />
                        {{ stat.change }}%
                    </div>
                </div>
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-container">
            <div class="chart-card">
                <div class="chart-header">
                    <h3>考试统计</h3>
                    <div class="chart-actions">
                        <Select v-model="examChartType" size="small" style="width: 100px;">
                            <Option value="pie">饼图</Option>
                            <Option value="bar">柱状图</Option>
                        </Select>
                    </div>
                </div>
                <div class="chart-content">
                    <v-chart 
                        :option="examChartOption" 
                        :style="{ height: '300px' }"
                        autoresize
                    />
                </div>
            </div>
            
            <div class="chart-card">
                <div class="chart-header">
                    <h3>用户活跃度</h3>
                    <div class="chart-actions">
                        <Select v-model="userChartType" size="small" style="width: 100px;">
                            <Option value="line">折线图</Option>
                            <Option value="area">面积图</Option>
                        </Select>
                    </div>
                </div>
                <div class="chart-content">
                    <v-chart 
                        :option="userChartOption" 
                        :style="{ height: '300px' }"
                        autoresize
                    />
                </div>
            </div>
        </div>

        <!-- 成绩分布图表 -->
        <div class="charts-container">
            <div class="chart-card full-width">
                <div class="chart-header">
                    <h3>成绩分布分析</h3>
                    <div class="chart-actions">
                        <Select v-model="scoreChartType" size="small" style="width: 120px;">
                            <Option value="histogram">直方图</Option>
                            <Option value="boxplot">箱线图</Option>
                        </Select>
                    </div>
                </div>
                <div class="chart-content">
                    <v-chart 
                        :option="scoreChartOption" 
                        :style="{ height: '350px' }"
                        autoresize
                    />
                </div>
            </div>
        </div>

        <!-- 通知中心和最近活动 -->
        <div class="bottom-section">
            <div class="notification-section">
                <NotificationCenter />
            </div>
            <div class="activity-section">
                <div class="recent-activity">
                    <h3>最近活动</h3>
                    <div class="activity-list">
                        <div class="activity-item" v-for="activity in activities" :key="activity.id">
                            <div class="activity-icon" :style="{ background: activity.color }">
                                <Icon :type="activity.icon" />
                            </div>
                            <div class="activity-content">
                                <div class="activity-title">{{ activity.title }}</div>
                                <div class="activity-time">{{ activity.time }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, HistogramChart } from 'echarts/charts'
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import RealTimeMonitor from './RealTimeMonitor.vue'
import NotificationCenter from './NotificationCenter.vue'

use([
    CanvasRenderer,
    PieChart,
    BarChart,
    LineChart,
    HistogramChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent
])

export default {
    name: 'Dashboard',
    components: {
        VChart,
        RealTimeMonitor,
        NotificationCenter
    },
    data() {
        return {
            stats: [
                { id: 1, label: '总学生数', value: '1,234', change: 12, trend: 'up', icon: 'ios-people', color: 'linear-gradient(135deg, #1890ff 0%, #0050b3 100%)' },
                { id: 2, label: '进行中考试', value: '8', change: 5, trend: 'up', icon: 'ios-document', color: 'linear-gradient(135deg, #19be6b 0%, #2db7f5 100%)' },
                { id: 3, label: '今日登录', value: '156', change: 8, trend: 'down', icon: 'ios-log-in', color: 'linear-gradient(135deg, #ff9900 0%, #ed4014 100%)' },
                { id: 4, label: '系统负载', value: '67%', change: 3, trend: 'up', icon: 'ios-speedometer', color: 'linear-gradient(135deg, #2db7f5 0%, #19be6b 100%)' }
            ],
            activities: [
                { id: 1, title: '张三完成了数学考试', time: '2分钟前', icon: 'ios-checkmark-circle', color: '#19be6b' },
                { id: 2, title: '李老师创建了新考试', time: '5分钟前', icon: 'ios-add-circle', color: '#2db7f5' },
                { id: 3, title: '系统自动备份完成', time: '10分钟前', icon: 'ios-cloud-upload', color: '#ff9900' },
                { id: 4, title: '王同学登录系统', time: '15分钟前', icon: 'ios-person', color: '#1890ff' }
            ],
            examChartType: 'pie',
            userChartType: 'line',
            scoreChartType: 'histogram'
        }
    },
    computed: {
        examChartOption() {
            if (this.examChartType === 'pie') {
                return {
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b}: {c} ({d}%)'
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        textStyle: {
                            color: '#666'
                        }
                    },
                    series: [
                        {
                            name: '考试状态',
                            type: 'pie',
                            radius: ['40%', '70%'],
                            avoidLabelOverlap: false,
                            label: {
                                show: false,
                                position: 'center'
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    fontSize: '18',
                                    fontWeight: 'bold'
                                }
                            },
                            labelLine: {
                                show: false
                            },
                            data: [
                                { value: 35, name: '已完成', itemStyle: { color: '#19be6b' } },
                                { value: 8, name: '进行中', itemStyle: { color: '#2db7f5' } },
                                { value: 12, name: '待开始', itemStyle: { color: '#ff9900' } },
                                { value: 5, name: '已过期', itemStyle: { color: '#ed4014' } }
                            ]
                        }
                    ]
                }
            } else {
                return {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        data: ['已完成', '进行中', '待开始', '已过期'],
                        axisLabel: {
                            color: '#666'
                        }
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            color: '#666'
                        }
                    },
                    series: [
                        {
                            name: '考试数量',
                            type: 'bar',
                            data: [
                                { value: 35, itemStyle: { color: '#19be6b' } },
                                { value: 8, itemStyle: { color: '#2db7f5' } },
                                { value: 12, itemStyle: { color: '#ff9900' } },
                                { value: 5, itemStyle: { color: '#ed4014' } }
                            ],
                            barWidth: '40%'
                        }
                    ]
                }
            }
        },
        userChartOption() {
            const data = [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330, 310, 123, 442, 321, 90, 149, 210, 122, 133, 334, 198, 123, 125, 220, 332, 301, 334, 390, 330, 220]
            const dates = []
            for (let i = 0; i < 31; i++) {
                dates.push(`${i + 1}日`)
            }

            if (this.userChartType === 'line') {
                return {
                    tooltip: {
                        trigger: 'axis'
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: dates,
                        axisLabel: {
                            color: isDark ? '#fff' : '#666',
                            interval: 2
                        }
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    series: [
                        {
                            name: '活跃用户',
                            type: 'line',
                            data: data,
                            smooth: true,
                            lineStyle: {
                                color: '#1890ff',
                                width: 3
                            },
                            areaStyle: {
                                color: {
                                    type: 'linear',
                                    x: 0,
                                    y: 0,
                                    x2: 0,
                                    y2: 1,
                                    colorStops: [
                                        { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                                        { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
                                    ]
                                }
                            }
                        }
                    ]
                }
            } else {
                return {
                    tooltip: {
                        trigger: 'axis'
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: dates,
                        axisLabel: {
                            color: isDark ? '#fff' : '#666',
                            interval: 2
                        }
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    series: [
                        {
                            name: '活跃用户',
                            type: 'line',
                            data: data,
                            smooth: true,
                            lineStyle: {
                                color: '#1890ff',
                                width: 3
                            },
                            areaStyle: {
                                color: {
                                    type: 'linear',
                                    x: 0,
                                    y: 0,
                                    x2: 0,
                                    y2: 1,
                                    colorStops: [
                                        { offset: 0, color: 'rgba(24, 144, 255, 0.6)' },
                                        { offset: 1, color: 'rgba(24, 144, 255, 0.2)' }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        },
        scoreChartOption() {
            if (this.scoreChartType === 'histogram') {
                return {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'category',
                        data: ['0-60', '60-70', '70-80', '80-90', '90-100'],
                        axisLabel: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    yAxis: {
                        type: 'value',
                        name: '学生人数',
                        axisLabel: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    series: [
                        {
                            name: '成绩分布',
                            type: 'bar',
                            data: [
                                { value: 45, itemStyle: { color: '#ed4014' } },
                                { value: 78, itemStyle: { color: '#ff9900' } },
                                { value: 156, itemStyle: { color: '#2db7f5' } },
                                { value: 234, itemStyle: { color: '#19be6b' } },
                                { value: 89, itemStyle: { color: '#1890ff' } }
                            ],
                            barWidth: '60%'
                        }
                    ]
                }
            } else {
                return {
                    tooltip: {
                        trigger: 'item',
                        formatter: function(params) {
                            return `${params.name}<br/>最小值: ${params.data[1]}<br/>下四分位数: ${params.data[2]}<br/>中位数: ${params.data[3]}<br/>上四分位数: ${params.data[4]}<br/>最大值: ${params.data[5]}`
                        }
                    },
                    grid: {
                        left: '10%',
                        right: '10%',
                        bottom: '15%'
                    },
                    xAxis: {
                        type: 'category',
                        data: ['数学', '语文', '英语', '物理', '化学'],
                        axisLabel: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    yAxis: {
                        type: 'value',
                        name: '分数',
                        axisStyle: {
                            color: isDark ? '#fff' : '#666'
                        }
                    },
                    series: [
                        {
                            name: '成绩分布',
                            type: 'boxplot',
                            data: [
                                [60, 70, 80, 85, 95],
                                [65, 75, 82, 88, 92],
                                [70, 78, 85, 90, 98],
                                [55, 68, 75, 82, 88],
                                [62, 72, 78, 85, 90]
                            ],
                            itemStyle: {
                                color: '#1890ff',
                                borderColor: '#2db7f5'
                            }
                        }
                    ]
                }
            }
        }
    }
}
</script>

<style scoped>
.dashboard {
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
}

.dashboard-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.dashboard-header h2 {
    margin: 0 0 10px 0;
    color: #2c3e50;
    font-size: 28px;
    font-weight: 600;
}

.dashboard-header p {
    margin: 0;
    color: #7f8c8d;
    font-size: 16px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    display: flex;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20px;
    color: white;
    font-size: 24px;
}

.stat-content {
    flex: 1;
}

.stat-number {
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 5px;
}

.stat-label {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 8px;
}

.stat-change {
    display: flex;
    align-items: center;
    font-size: 12px;
    font-weight: 500;
}

.stat-change.up {
    color: #19be6b;
}

.stat-change.down {
    color: #ed4014;
}

.stat-change i {
    margin-right: 4px;
}

.charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.chart-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.chart-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.chart-card.full-width {
    grid-column: 1 / -1;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.chart-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 18px;
    font-weight: 600;
}

.chart-content {
    border-radius: 10px;
    overflow: hidden;
}

.recent-activity {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.recent-activity h3 {
    margin: 0 0 20px 0;
    color: #2c3e50;
    font-size: 18px;
    font-weight: 600;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.activity-item {
    display: flex;
    align-items: center;
    padding: 15px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 10px;
    transition: all 0.3s ease;
}

.activity-item:hover {
    background: rgba(255, 255, 255, 0.8);
    transform: translateX(5px);
}

.activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    color: white;
    font-size: 16px;
}

.activity-content {
    flex: 1;
}

.activity-title {
    color: #2c3e50;
    font-weight: 500;
    margin-bottom: 5px;
}

.activity-time {
    color: #7f8c8d;
    font-size: 12px;
}

/* 深色主题适配 */
.dark-theme .dashboard {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

.dark-theme .dashboard-header,
.dark-theme .stat-card,
.dark-theme .chart-card,
.dark-theme .recent-activity {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
}

.dark-theme .dashboard-header h2,
.dark-theme .dashboard-header p,
.dark-theme .stat-number,
.dark-theme .chart-header h3,
.dark-theme .recent-activity h3,
.dark-theme .activity-title {
    color: #fff;
}

.dark-theme .stat-label,
.dark-theme .activity-time {
    color: #bdc3c7;
}

.dark-theme .activity-item {
    background: rgba(255, 255, 255, 0.05);
}

.dark-theme .activity-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* 底部区域布局 */
.bottom-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    margin-top: 30px;
}

.notification-section {
    min-height: 400px;
}

.activity-section {
    min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .dashboard {
        padding: 15px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .chart-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .stat-card {
        padding: 20px;
    }
    
    .stat-icon {
        width: 50px;
        height: 50px;
        font-size: 20px;
    }
    
    .stat-number {
        font-size: 24px;
    }
    
    .bottom-section {
        grid-template-columns: 1fr;
        gap: 15px;
    }
}
</style>
