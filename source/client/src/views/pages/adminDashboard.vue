<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <div class="header-left">
        <h1>管理员仪表板</h1>
        <p>系统运行状态概览</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <Spin v-if="loading" fix>
      <Icon type="ios-loading" size="48" class="spin-icon-load"></Icon>
      <div>加载中...</div>
    </Spin>

    <!-- 今日学习行为速览 -->
    <div class="today-highlights">
      <h2>今日学习行为速览</h2>
      <div class="highlights-grid">
        <div class="highlight-card">
          <div class="highlight-icon practice">
            <i class="ivu-icon ivu-icon-ios-book"></i>
          </div>
          <div class="highlight-content">
            <div class="highlight-number">{{ dashboardData.today?.completed_practices || 0 }}</div>
            <div class="highlight-label">今日完成练习</div>
            <div class="highlight-desc">共 {{ dashboardData.today?.practices || 0 }} 次练习</div>
          </div>
        </div>
        <div class="highlight-card">
          <div class="highlight-icon task">
            <i class="ivu-icon ivu-icon-ios-list"></i>
          </div>
          <div class="highlight-content">
            <div class="highlight-number">{{ dashboardData.today?.completed_tasks || 0 }}</div>
            <div class="highlight-label">今日完成任务</div>
            <div class="highlight-desc">共 {{ dashboardData.today?.tasks || 0 }} 个任务</div>
          </div>
        </div>
        <div class="highlight-card">
          <div class="highlight-icon ai">
            <i class="ivu-icon ivu-icon-ios-flash"></i>
          </div>
          <div class="highlight-content">
            <div class="highlight-number">{{ dashboardData.today?.ai_scoring || 0 }}</div>
            <div class="highlight-label">今日AI分析次数</div>
            <div class="highlight-desc">智能评分与反馈</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">
          <i class="ivu-icon ivu-icon-ios-people"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_users || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon students">
          <i class="ivu-icon ivu-icon-ios-school"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_students || 0 }}</div>
          <div class="stat-label">学生数量</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon teachers">
          <i class="ivu-icon ivu-icon-ios-person"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_teachers || 0 }}</div>
          <div class="stat-label">教师数量</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon admins">
          <i class="ivu-icon ivu-icon-ios-settings"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_admins || 0 }}</div>
          <div class="stat-label">管理员数量</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon exams">
          <i class="ivu-icon ivu-icon-ios-document"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_exams || 0 }}</div>
          <div class="stat-label">试卷总数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon questions">
          <i class="ivu-icon ivu-icon-ios-help-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_questions || 0 }}</div>
          <div class="stat-label">题目总数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon tasks">
          <i class="ivu-icon ivu-icon-ios-list"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.total_tasks || 0 }}</div>
          <div class="stat-label">任务总数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon active">
          <i class="ivu-icon ivu-icon-ios-pulse"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.activity?.active_users || 0 }}</div>
          <div class="stat-label">活跃用户</div>
          <div class="stat-desc">最近7天有学习行为</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon ai-scoring">
          <i class="ivu-icon ivu-icon-ios-flash"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.ai_scoring_count || 0 }}</div>
          <div class="stat-label">AI评分次数</div>
          <div class="stat-desc">累计智能评分总数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pass-rate">
          <i class="ivu-icon ivu-icon-ios-checkmark-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ dashboardData.overview?.pass_rate || 0 }}%</div>
          <div class="stat-label">通过率</div>
          <div class="stat-desc">最近7天平均通过率</div>
        </div>
      </div>
    </div>

    <!-- 趋势图 -->
    <div class="trends-section">
      <h2>最近7天学习趋势</h2>
      <div class="trends-chart" ref="trendsChart"></div>
    </div>

    <!-- 本月统计 -->
    <div class="monthly-stats">
      <h2>本月新增</h2>
      <div class="monthly-grid">
        <div class="monthly-item">
          <div class="monthly-number">{{ dashboardData.monthly?.new_users || 0 }}</div>
          <div class="monthly-label">新增用户</div>
        </div>
        <div class="monthly-item">
          <div class="monthly-number">{{ dashboardData.monthly?.new_exams || 0 }}</div>
          <div class="monthly-label">新增试卷</div>
        </div>
        <div class="monthly-item">
          <div class="monthly-number">{{ dashboardData.monthly?.new_questions || 0 }}</div>
          <div class="monthly-label">新增题目</div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="actions-grid">
        <div class="action-item" @click="navigateTo('/admin/users')">
          <i class="ivu-icon ivu-icon-ios-people"></i>
          <span>用户管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/subjects')">
          <i class="ivu-icon ivu-icon-ios-book"></i>
          <span>学科管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/exams')">
          <i class="ivu-icon ivu-icon-ios-document"></i>
          <span>试卷管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/questions')">
          <i class="ivu-icon ivu-icon-ios-help-circle"></i>
          <span>题目管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/tasks')">
          <i class="ivu-icon ivu-icon-ios-list"></i>
          <span>任务管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/messages')">
          <i class="ivu-icon ivu-icon-ios-mail"></i>
          <span>消息管理</span>
        </div>
        <div class="action-item" @click="navigateTo('/admin/logs')">
          <i class="ivu-icon ivu-icon-ios-analytics"></i>
          <span>系统日志</span>
        </div>
      </div>
    </div>

    <!-- 数据管理 -->
    <div class="data-management">
      <h2>数据管理</h2>
      <div class="data-actions">
        <Upload
          :show-upload-list="false"
          :before-upload="handleBeforeStudentImport"
          action="#"
        >
          <Button type="primary" icon="ios-upload" :loading="importing" size="large">
            批量导入学生
          </Button>
        </Upload>
        <Button @click="downloadStudentTemplate" icon="ios-download-outline" size="large">
          下载学生模板
        </Button>
        <Button @click="exportStudents" icon="ios-cloud-download-outline" size="large">
          导出学生数据
        </Button>
        <Button @click="exportTeachers" icon="ios-people" size="large">
          导出教师数据
        </Button>
        <Button @click="openExamStatModal" icon="ios-stats" size="large">
          考试统计/导出
        </Button>
      </div>
    </div>

    <!-- 考试统计与导出 -->
    <Modal v-model="examStatModal" title="考试统计/导出" width="480">
      <div class="exam-stat-body">
        <Input v-model="examStatId" placeholder="请输入考试ID" style="margin-bottom: 12px" />
        <div class="stat-actions">
          <Button type="primary" icon="ios-stats" @click="fetchExamStatistics">获取统计</Button>
          <Button icon="ios-download-outline" @click="exportExamResults">导出考试结果</Button>
        </div>
        <div v-if="examStatResult" class="stat-result">
          <p><strong>考试：</strong>{{ examStatResult.exam_name || examStatResult.exam_id }}</p>
          <p><strong>人数：</strong>{{ examStatResult.completed_students }}/{{ examStatResult.total_students }}（完成率 {{ examStatResult.completion_rate }}%）</p>
          <p><strong>平均分：</strong>{{ examStatResult.avg_score }}，最高 {{ examStatResult.max_score }}，最低 {{ examStatResult.min_score }}</p>
          <p><strong>分布：</strong>
            优秀 {{ examStatResult.score_distribution?.excellent || 0 }}；
            良好 {{ examStatResult.score_distribution?.good || 0 }}；
            中等 {{ examStatResult.score_distribution?.medium || 0 }}；
            不及格 {{ examStatResult.score_distribution?.poor || 0 }}
          </p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import {
  getAdminDashboard,
  importAdminStudents,
  downloadStudentsTemplate,
  exportAdminStudents,
  exportAdminTeachers,
  exportAdminExamResults,
  getAdminExamStatistics
} from '@/api/index.js'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

export default {
  name: 'AdminDashboard',
  data() {
    return {
      loading: false,
      importing: false,
      examStatModal: false,
      examStatId: '',
      examStatResult: null,
      dashboardData: {
        overview: {},
        monthly: {},
        activity: {},
        today: {},
        trends_7d: {
          days: [],
          practices: [],
          tasks: []
        }
      },
      trendsChart: null,
      resizeHandler: null
    }
  },
  methods: {
    async handleBeforeStudentImport(file) {
      this.importing = true
      try {
        const fd = new FormData()
        fd.append('file', file)
        const resp = await importAdminStudents(fd)
        if (resp.code === 0) {
          const { success = 0, fail = 0, errors = [] } = resp.data || {}
          this.$Message.success(`导入完成：成功 ${success} 条，失败 ${fail} 条`)
          if (errors.length) {
            console.warn('导入错误详情', errors)
          }
        } else {
          this.$Message.error(resp.msg || '导入失败')
        }
      } catch (e) {
        console.error('导入失败', e)
        this.$Message.error('导入失败')
      } finally {
        this.importing = false
      }
      return false
    },
    async downloadStudentTemplate() {
      try {
        const resp = await downloadStudentsTemplate()
        // 检查响应状态
        if (resp.code !== undefined && resp.code !== 0) {
          this.$Message.error(resp.msg || '下载模板失败')
          return
        }
        const blob = new Blob([resp.data || resp], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'students_template.xlsx'
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        console.error('下载模板失败', e)
        this.$Message.error('下载模板失败')
      }
    },
    async exportStudents() {
      try {
        const resp = await exportAdminStudents()
        const blob = new Blob([resp.data || resp], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'students.csv'
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        console.error('导出学生失败', e)
        this.$Message.error('导出学生失败')
      }
    },
    async exportTeachers() {
      try {
        const resp = await exportAdminTeachers()
        const blob = new Blob([resp.data || resp], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'teachers.csv'
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        console.error('导出教师失败', e)
        this.$Message.error('导出教师失败')
      }
    },
    openExamStatModal() {
      this.examStatModal = true
      this.examStatResult = null
    },
    async fetchExamStatistics() {
      if (!this.examStatId) {
        this.$Message.warning('请输入考试ID')
        return
      }
      try {
        const resp = await getAdminExamStatistics(this.examStatId)
        if (resp.code === 0) {
          this.examStatResult = resp.data
        } else {
          this.$Message.error(resp.msg || '获取统计失败')
        }
      } catch (e) {
        console.error('获取统计失败', e)
        this.$Message.error('获取统计失败')
      }
    },
    async exportExamResults() {
      if (!this.examStatId) {
        this.$Message.warning('请输入考试ID')
        return
      }
      try {
        const resp = await exportAdminExamResults(this.examStatId)
        const blob = new Blob([resp.data || resp], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `exam_${this.examStatId}_results.csv`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        console.error('导出考试结果失败', e)
        this.$Message.error('导出考试结果失败')
      }
    },
    async loadDashboardData() {
      try {
        this.loading = true
        const response = await getAdminDashboard()
        if (response.code === 0) {
          this.dashboardData = response.data
          this.$nextTick(() => {
            this.initTrendsChart()
          })
        } else {
          this.$Message.error(response.msg || '获取仪表板数据失败')
        }
      } catch (error) {
        console.error('获取仪表板数据失败:', error)
        this.$Message.error('获取仪表板数据失败')
      } finally {
        this.loading = false
      }
    },
    initTrendsChart() {
      if (!this.$refs.trendsChart) return
      
      if (this.trendsChart) {
        this.trendsChart.dispose()
      }

      // 检查DOM元素是否存在
      if (!this.$refs.trendsChart) {
        console.error('图表容器未找到')
        return
      }

      this.trendsChart = echarts.init(this.$refs.trendsChart)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['完成练习数', '完成任务数'],
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.dashboardData.trends_7d?.days || [],
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0'
            }
          }
        },
        series: [
          {
            name: '完成练习数',
            type: 'line',
            data: this.dashboardData.trends_7d?.practices || [],
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#2d8cf0'
            },
            itemStyle: {
              color: '#2d8cf0'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(45, 140, 240, 0.3)' },
                  { offset: 1, color: 'rgba(45, 140, 240, 0.05)' }
                ]
              }
            }
          },
          {
            name: '完成任务数',
            type: 'line',
            data: this.dashboardData.trends_7d?.tasks || [],
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#19be6b'
            },
            itemStyle: {
              color: '#19be6b'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(25, 190, 107, 0.3)' },
                  { offset: 1, color: 'rgba(25, 190, 107, 0.05)' }
                ]
              }
            }
          }
        ]
      }
      
      this.trendsChart.setOption(option)

      // 响应式调整 - 保存处理器引用
      this.resizeHandler = () => {
        if (this.trendsChart) {
          this.trendsChart.resize()
        }
      }
      window.addEventListener('resize', this.resizeHandler)
    },
    navigateTo(path) {
      this.$router.push(path)
    }
  },
  mounted() {
    this.loadDashboardData()
  },
  beforeUnmount() {
    if (this.trendsChart) {
      this.trendsChart.dispose()
      this.trendsChart = null
    }
    // 移除事件监听器
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler)
      this.resizeHandler = null
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 24px;
  background: linear-gradient(135deg, #fff7f0 0%, #fff 100%);
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

/* Dashboard头部 - 橙色渐变主题 */
.dashboard-header {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(250, 140, 22, 0.3);
}

.dashboard-header h1 {
  font-size: 28px;
  color: #fff;
  margin-bottom: 8px;
  font-weight: 600;
}

.dashboard-header p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.exam-stat-body .stat-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.exam-stat-body .stat-result p {
  margin: 4px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #e8eaec;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

/* 统一颜色方案：4个主色系 */
.stat-icon.users,
.stat-icon.ai-scoring { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
}
.stat-icon.students,
.stat-icon.exams { 
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
}
.stat-icon.teachers,
.stat-icon.questions { 
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
}
.stat-icon.admins,
.stat-icon.pass-rate { 
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
}
.stat-icon.tasks { 
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
}
.stat-icon.active { 
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #17233d;
  margin-bottom: 4px;
}

.stat-label {
  color: #808695;
  font-size: 14px;
  margin-bottom: 2px;
}

.stat-desc {
  color: #c5c8ce;
  font-size: 12px;
}

.today-highlights {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaec;
}

.today-highlights h2 {
  color: #17233d;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.today-highlights h2::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  margin-right: 12px;
  border-radius: 2px;
}

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.highlight-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.highlight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.highlight-card:nth-child(1) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.highlight-card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.highlight-card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.highlight-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  background: rgba(255, 255, 255, 0.2);
}

.highlight-content {
  flex: 1;
}

.highlight-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 4px;
}

.highlight-label {
  font-size: 16px;
  margin-bottom: 4px;
  opacity: 0.95;
}

.highlight-desc {
  font-size: 12px;
  opacity: 0.8;
}

.trends-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaec;
}

.trends-section h2 {
  color: #17233d;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.trends-section h2::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-right: 12px;
  border-radius: 2px;
}

.trends-chart {
  width: 100%;
  height: 400px;
  margin-top: 10px;
}

.monthly-stats {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaec;
}

.monthly-stats h2 {
  color: #17233d;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.monthly-stats h2::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  margin-right: 12px;
  border-radius: 2px;
}

.monthly-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.monthly-item {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  transition: all 0.2s;
  border: 1px solid #e8eaec;
}

.monthly-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
}

.monthly-number {
  font-size: 28px;
  font-weight: bold;
  color: #19be6b;
  margin-bottom: 8px;
}

.monthly-label {
  color: #808695;
  font-size: 14px;
}

.quick-actions {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaec;
}

.spin-icon-load {
  animation: ani-spin 1s linear infinite;
}

@keyframes ani-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.quick-actions h2 {
  color: #17233d;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.quick-actions h2::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  margin-right: 12px;
  border-radius: 2px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e8eaec;
}

.action-item:hover {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(45, 140, 240, 0.2);
  border-color: #2d8cf0;
}

.action-item i {
  font-size: 24px;
  color: #2d8cf0;
  margin-bottom: 8px;
}

.action-item span {
  color: #17233d;
  font-size: 14px;
  text-align: center;
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .highlights-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .trends-chart {
    height: 280px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 12px;
  }
}

.data-management {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaec;
}

.data-management h2 {
  color: #17233d;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.data-management h2::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  margin-right: 12px;
  border-radius: 2px;
}

.data-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.data-actions .ivu-btn {
  margin: 0;
}

@media (max-width: 768px) {
  .data-actions {
    flex-direction: column;
  }
  
  .data-actions .ivu-btn {
    width: 100%;
  }
}
</style>





