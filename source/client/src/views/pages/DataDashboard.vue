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
import http from '@/utils/http'

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
      trendDays: [],
      practiceTrend: [],
      taskTrend: [],
      questionTypeData: [],
      subjectData: [],
      activityDays: [],
      activityData: [],
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
        const data = await http.get('/admin/dashboard/')
        if (data.code === 0 && data.data) {
          const overview = data.data.overview || {}
          const trends7d = data.data.trends_7d || {}
          this.stats = {
            totalStudents: overview.total_students || 0,
            totalTeachers: overview.total_teachers || 0,
            totalQuestions: overview.total_questions || 0,
            totalExams: overview.total_exams || 0
          }
          this.trendDays = trends7d.days || []
          this.practiceTrend = trends7d.practices || []
          this.taskTrend = trends7d.tasks || []

          this.activityDays = this.trendDays.length ? [...this.trendDays] : ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
          this.activityData = this.practiceTrend.map((value, index) => (Number(value) || 0) + (Number(this.taskTrend[index]) || 0))
        }
      } catch (e) {
        console.error('加载看板数据失败', e)
      }

      await this.loadGradeRanking()
      await this.loadRecentExams()
      await this.loadActiveStudents()
      await this.loadQuestionAndSubjectData()
      this.$nextTick(() => {
        this.renderCharts()
      })
    },
    async loadGradeRanking() {
      try {
        const gradesResp = await http.get('/grades/all/')
        const grades = (gradesResp.code === 0 && gradesResp.data) ? gradesResp.data : []
        const gradeIds = grades.map(g => g.id).slice(0, 10)

        if (gradeIds.length >= 2) {
          const compareResp = await http.get('/statistics/compare_classes/', {
            params: {
              gradeIds: gradeIds.join(',')
            }
          })
          if (compareResp.code === 0 && compareResp.data && compareResp.data.comparisonData) {
            this.gradeRanking = compareResp.data.comparisonData.slice(0, 5).map(item => ({
              id: item.gradeId,
              name: item.gradeName,
              avgScore: Number(item.examStats?.avgScore || 0)
            }))
          }
        }
      } catch (e) {
        console.error('加载班级排名失败', e)
      }

      if (!this.gradeRanking.length) {
        this.gradeRanking = []
      }
    },
    async loadRecentExams() {
      try {
        const data = await http.get('/exams/page/', {
          params: {
            pageIndex: 1,
            pageSize: 5
          }
        })
        if (data.code === 0) {
          const list = data.data?.data || data.data?.list || []
          this.recentExams = list.map(e => ({
            name: e.name,
            subject: e.projectName,
            participants: Number(e.participants || e.studentCount || 0),
            avgScore: Number(e.avgScore || 0)
          }))
        }
      } catch (e) {
        console.error('加载最近考试失败', e)
      }

      if (!this.recentExams.length) {
        this.recentExams = []
      }
    },
    async loadActiveStudents() {
      try {
        const data = await http.get('/students/page/', {
          params: {
            pageIndex: 1,
            pageSize: 5
          }
        })
        if (data.code === 0) {
          const list = data.data?.data || data.data?.list || []
          this.activeStudents = list.map(student => ({
            name: student.name,
            grade: student.gradeName || '',
            practiceCount: Number(student.practiceCount || 0),
            avgScore: Number(student.avgScore || 0)
          }))
        }
      } catch (e) {
        console.error('加载活跃学生失败', e)
      }

      if (!this.activeStudents.length) {
        this.activeStudents = []
      }
    },
    async loadQuestionAndSubjectData() {
      try {
        const data = await http.get('/practises/page/', {
          params: {
            pageIndex: 1,
            pageSize: 500,
            name: '',
            type: '',
            projectId: ''
          }
        })

        if (data.code === 0) {
          const list = data.data?.data || data.data?.list || []
          const typeNameMap = {
            0: '选择题',
            1: '填空题',
            2: '判断题',
            3: '编程题'
          }
          const typeColorMap = {
            '选择题': '#2d8cf0',
            '填空题': '#19be6b',
            '判断题': '#ff9900',
            '编程题': '#ed4014'
          }
          const subjectColorPool = ['#2d8cf0', '#19be6b', '#ff9900', '#ed4014', '#9b59b6', '#36cfc9']

          const typeCounter = {}
          const subjectCounter = {}

          list.forEach(item => {
            const typeName = typeNameMap[item.type] || '其他'
            typeCounter[typeName] = (typeCounter[typeName] || 0) + 1

            const subjectName = item.projectName || item.project || '未知学科'
            subjectCounter[subjectName] = (subjectCounter[subjectName] || 0) + 1
          })

          this.questionTypeData = Object.keys(typeCounter).map(name => ({
            value: typeCounter[name],
            name,
            itemStyle: { color: typeColorMap[name] || '#8c8c8c' }
          }))

          this.subjectData = Object.keys(subjectCounter)
            .map((name, index) => ({
              value: subjectCounter[name],
              name,
              itemStyle: { color: subjectColorPool[index % subjectColorPool.length] }
            }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 6)
        }
      } catch (e) {
        console.error('加载题型与学科分布失败', e)
      }

      if (!this.questionTypeData.length) {
        this.questionTypeData = []
      }
      if (!this.subjectData.length) {
        this.subjectData = []
      }
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
          data: ['练习完成数', '任务完成数']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.trendDays.length ? this.trendDays : ['近7天']
        },
        yAxis: {
          type: 'value',
          name: '次数'
        },
        series: [
          {
            name: '练习完成数',
            type: 'bar',
            data: this.practiceTrend.length ? this.practiceTrend : [0],
            itemStyle: { color: '#2d8cf0' }
          },
          {
            name: '任务完成数',
            type: 'line',
            data: this.taskTrend.length ? this.taskTrend : [0],
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
            data: this.questionTypeData.length ? this.questionTypeData : [{ value: 1, name: '暂无数据', itemStyle: { color: '#d9d9d9' } }],
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
          data: this.subjectData.length ? this.subjectData.map(item => item.name) : ['暂无数据']
        },
        series: [
          {
            type: 'bar',
            data: this.subjectData.length
              ? this.subjectData.map(item => ({ value: item.value, itemStyle: item.itemStyle }))
              : [{ value: 0, itemStyle: { color: '#d9d9d9' } }]
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
          data: this.activityDays.length ? this.activityDays : ['近7天']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            type: 'line',
            smooth: true,
            data: this.activityData.length ? this.activityData : [0],
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
  background: #ffffff;
  min-height: 100vh;
  padding: 20px;
  color: #000000;
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
  color: #000000;
}

.header-time {
  font-size: 18px;
  color: #000000;
}

.stat-card {
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e6ebf2;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
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
  color: #000000;
}

.stat-label {
  font-size: 14px;
  color: #000000;
  margin-top: 5px;
}

.chart-card,
.info-card {
  background: #ffffff;
  border: 1px solid #e6ebf2;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
  margin-bottom: 16px;
}

.chart-card >>> .ivu-card-head,
.info-card >>> .ivu-card-head {
  border-bottom: 1px solid #edf1f7;
  color: #000000;
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
  border-bottom: 1px solid #edf1f7;
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
  color: #000000;
}

.info-card >>> .ivu-table {
  background: transparent;
  color: #000000;
}

.info-card >>> .ivu-table th {
  background: #f8fafc;
  color: #000000;
}

.info-card >>> .ivu-table td {
  background: transparent;
  border-bottom: 1px solid #edf1f7;
}
</style>
