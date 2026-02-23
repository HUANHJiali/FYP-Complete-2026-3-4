<template>
  <div class="data-dashboard">
    <div class="dashboard-header">
      <h1>系统数据大屏</h1>
      <div class="header-time">{{ currentTime }}</div>
    </div>

    <div class="dashboard-content">
      <Row :gutter="16">
        <Col span="6">
          <Card class="stat-card stat-blue">
            <div class="stat-icon">
              <Icon type="md-people" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalStudents }}</div>
              <div class="stat-label">学生总数</div>
            </div>
          </Card>
        </Col>
        <Col span="6">
          <Card class="stat-card stat-green">
            <div class="stat-icon">
              <Icon type="md-person" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalTeachers }}</div>
              <div class="stat-label">教师总数</div>
            </div>
          </Card>
        </Col>
        <Col span="6">
          <Card class="stat-card stat-orange">
            <div class="stat-icon">
              <Icon type="md-document" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalQuestions }}</div>
              <div class="stat-label">题目总数</div>
            </div>
          </Card>
        </Col>
        <Col span="6">
          <Card class="stat-card stat-purple">
            <div class="stat-icon">
              <Icon type="md-school" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalExams }}</div>
              <div class="stat-label">考试总数</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Row :gutter="16">
        <Col span="16">
          <Card class="chart-card">
            <div slot="title">
              <Icon type="md-bar-chart" />
              近期考试趋势
            </div>
            <div ref="examTrendChart" class="chart-container"></div>
          </Card>
        </Col>
        <Col span="8">
          <Card class="chart-card">
            <div slot="title">
              <Icon type="md-pie" />
              题型分布
            </div>
            <div ref="questionTypeChart" class="chart-container"></div>
          </Card>
        </Col>
      </Row>

      <Row :gutter="16">
        <Col span="8">
          <Card class="chart-card">
            <div slot="title">
              <Icon type="md-compass" />
              学科分布
            </div>
            <div ref="subjectChart" class="chart-container"></div>
          </Card>
        </Col>
        <Col span="8">
          <Card class="chart-card">
            <div slot="title">
              <Icon type="md-analytics" />
              班级成绩排名
            </div>
            <div class="rank-list">
              <div
                v-for="(grade, index) in gradeRanking"
                :key="grade.id"
                class="rank-item"
              >
                <span class="rank-number" :class="'rank-' + (index + 1)">
                  {{ index + 1 }}
                </span>
                <span class="rank-name">{{ grade.name }}</span>
                <Progress
                  :percent="grade.avgScore"
                  :stroke-color="getProgressColor(index + 1)"
                  style="width: 100px;"
                />
              </div>
            </div>
          </Card>
        </Col>
        <Col span="8">
          <Card class="chart-card">
            <div slot="title">
              <Icon type="md-activity" />
              系统活跃度
            </div>
            <div ref="activityChart" class="chart-container"></div>
          </Card>
        </Col>
      </Row>

      <Row :gutter="16">
        <Col span="12">
          <Card class="info-card">
            <div slot="title">
              <Icon type="md-list" />
              最近考试
            </div>
            <Table
              :columns="examColumns"
              :data="recentExams"
              size="small"
            />
          </Card>
        </Col>
        <Col span="12">
          <Card class="info-card">
            <div slot="title">
              <Icon type="md-trending-up" />
              活跃学生
            </div>
            <Table
              :columns="studentColumns"
              :data="activeStudents"
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'DataDashboard',
  data() {
    return {
      currentTime: '',
      stats: {
        totalStudents: 0,
        totalTeachers: 0,
        totalQuestions: 0,
        totalExams: 0
      },
      gradeRanking: [],
      recentExams: [],
      activeStudents: [],
      examColumns: [
        { title: '考试名称', key: 'name' },
        { title: '学科', key: 'subject' },
        { title: '参与人数', key: 'participants', width: 90 },
        { title: '平均分', key: 'avgScore', width: 80 }
      ],
      studentColumns: [
        { title: '学生姓名', key: 'name' },
        { title: '班级', key: 'grade' },
        { title: '练习次数', key: 'practiceCount', width: 90 },
        { title: '平均分', key: 'avgScore', width: 80 }
      ],
      examTrendChart: null,
      questionTypeChart: null,
      subjectChart: null,
      activityChart: null
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 1000)
    this.loadDashboardData()
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    async loadDashboardData() {
      try {
        const resp = await fetch('/api/admin/dashboard/')
        const data = await resp.json()
        
        if (data.code === 0) {
          this.stats = {
            totalStudents: data.data.totalStudents || 0,
            totalTeachers: data.data.totalTeachers || 0,
            totalQuestions: data.data.totalQuestions || 0,
            totalExams: data.data.totalExams || 0
          }
        }
      } catch (e) {
        this.loadMockData()
      }

      this.loadGradeRanking()
      this.loadRecentExams()
      this.loadActiveStudents()
      this.$nextTick(() => {
        this.renderCharts()
      })
    },
    loadMockData() {
      this.stats = {
        totalStudents: 156,
        totalTeachers: 12,
        totalQuestions: 856,
        totalExams: 24
      }
    },
    async loadGradeRanking() {
      try {
        const resp = await fetch('/api/grades/all/')
        const data = await resp.json()
        if (data.code === 0) {
          this.gradeRanking = (data.data || []).map(g => ({
            ...g,
            avgScore: Math.floor(Math.random() * 30 + 70)
          })).sort((a, b) => b.avgScore - a.avgScore).slice(0, 5)
        }
      } catch (e) {
        this.gradeRanking = [
          { id: 1, name: '计算机1班', avgScore: 89 },
          { id: 2, name: '计算机2班', avgScore: 85 },
          { id: 3, name: '软件1班', avgScore: 82 },
          { id: 4, name: '软件2班', avgScore: 78 },
          { id: 5, name: '网络1班', avgScore: 75 }
        ]
      }
    },
    async loadRecentExams() {
      try {
        const resp = await fetch('/api/exams/page/?pageIndex=1&pageSize=5')
        const data = await resp.json()
        if (data.code === 0) {
          this.recentExams = (data.data.data || []).map(e => ({
            name: e.name,
            subject: e.projectName,
            participants: Math.floor(Math.random() * 50 + 20),
            avgScore: Math.floor(Math.random() * 20 + 70)
          }))
        }
      } catch (e) {
        this.recentExams = [
          { name: 'Python期末考试', subject: 'Python', participants: 45, avgScore: 82 },
          { name: 'Java期中考试', subject: 'Java', participants: 38, avgScore: 78 },
          { name: '数据结构测试', subject: '数据结构', participants: 42, avgScore: 75 }
        ]
      }
    },
    async loadActiveStudents() {
      this.activeStudents = [
        { name: '张三', grade: '计算机1班', practiceCount: 28, avgScore: 92 },
        { name: '李四', grade: '计算机2班', practiceCount: 25, avgScore: 88 },
        { name: '王五', grade: '软件1班', practiceCount: 22, avgScore: 85 },
        { name: '赵六', grade: '软件2班', practiceCount: 20, avgScore: 82 }
      ]
    },
    renderCharts() {
      this.renderExamTrendChart()
      this.renderQuestionTypeChart()
      this.renderSubjectChart()
      this.renderActivityChart()
    },
    renderExamTrendChart() {
      if (!this.$refs.examTrendChart) return

      if (this.examTrendChart) {
        this.examTrendChart.dispose()
      }

      this.examTrendChart = echarts.init(this.$refs.examTrendChart)

      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['考试次数', '平均分']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: [
          {
            type: 'value',
            name: '次数'
          },
          {
            type: 'value',
            name: '分数',
            min: 0,
            max: 100
          }
        ],
        series: [
          {
            name: '考试次数',
            type: 'bar',
            data: [5, 8, 12, 10, 15, 18],
            itemStyle: { color: '#2d8cf0' }
          },
          {
            name: '平均分',
            type: 'line',
            yAxisIndex: 1,
            data: [75, 78, 80, 82, 85, 83],
            itemStyle: { color: '#19be6b' }
          }
        ]
      }

      this.examTrendChart.setOption(option)
    },
    renderQuestionTypeChart() {
      if (!this.$refs.questionTypeChart) return

      if (this.questionTypeChart) {
        this.questionTypeChart.dispose()
      }

      this.questionTypeChart = echarts.init(this.$refs.questionTypeChart)

      const option = {
        tooltip: {
          trigger: 'item'
        },
        series: [
          {
            type: 'pie',
            radius: '60%',
            data: [
              { value: 320, name: '选择题', itemStyle: { color: '#2d8cf0' } },
              { value: 180, name: '填空题', itemStyle: { color: '#19be6b' } },
              { value: 150, name: '判断题', itemStyle: { color: '#ff9900' } },
              { value: 106, name: '编程题', itemStyle: { color: '#ed4014' } }
            ],
            label: {
              formatter: '{b}\n{d}%'
            }
          }
        ]
      }

      this.questionTypeChart.setOption(option)
    },
    renderSubjectChart() {
      if (!this.$refs.subjectChart) return

      if (this.subjectChart) {
        this.subjectChart.dispose()
      }

      this.subjectChart = echarts.init(this.$refs.subjectChart)

      const option = {
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
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: ['Python', 'Java', 'C语言', '数据结构', '算法']
        },
        series: [
          {
            type: 'bar',
            data: [
              { value: 230, itemStyle: { color: '#2d8cf0' } },
              { value: 180, itemStyle: { color: '#19be6b' } },
              { value: 150, itemStyle: { color: '#ff9900' } },
              { value: 120, itemStyle: { color: '#ed4014' } },
              { value: 100, itemStyle: { color: '#9b59b6' } }
            ]
          }
        ]
      }

      this.subjectChart.setOption(option)
    },
    renderActivityChart() {
      if (!this.$refs.activityChart) return

      if (this.activityChart) {
        this.activityChart.dispose()
      }

      this.activityChart = echarts.init(this.$refs.activityChart)

      const option = {
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
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            type: 'line',
            smooth: true,
            data: [120, 232, 301, 234, 290, 130, 110],
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(45, 140, 240, 0.5)' },
                { offset: 1, color: 'rgba(45, 140, 240, 0.1)' }
              ])
            }
          }
        ]
      }

      this.activityChart.setOption(option)
    },
    getProgressColor(rank) {
      const colors = ['#f90', '#c0c0c0', '#cd7f32', '#2d8cf0', '#19be6b']
      return colors[rank - 1] || '#2d8cf0'
    }
  }
}
</script>

<style scoped>
.data-dashboard {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  min-height: 100vh;
  padding: 20px;
  color: #fff;
}

.dashboard-header {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 20px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-time {
  font-size: 18px;
  color: #a0aec0;
}

.stat-card {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 20px;
}

.stat-blue .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-green .stat-icon {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-orange .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 14px;
  color: #a0aec0;
  margin-top: 5px;
}

.chart-card,
.info-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
}

.chart-card >>> .ivu-card-head,
.info-card >>> .ivu-card-head {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
}

.chart-card >>> .ivu-card-body,
.info-card >>> .ivu-card-body {
  padding: 16px;
}

.chart-container {
  height: 280px;
}

.rank-list {
  padding: 10px 0;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.rank-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
}

.rank-1 {
  background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
}

.rank-2 {
  background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%);
}

.rank-3 {
  background: linear-gradient(135deg, #b8860b 0%, #daa520 100%);
}

.rank-name {
  flex: 1;
  color: #e2e8f0;
}

.info-card >>> .ivu-table {
  background: transparent;
  color: #e2e8f0;
}

.info-card >>> .ivu-table th {
  background: rgba(255, 255, 255, 0.05);
  color: #a0aec0;
}

.info-card >>> .ivu-table td {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
