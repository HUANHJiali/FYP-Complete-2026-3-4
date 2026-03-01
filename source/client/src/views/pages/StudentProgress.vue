<template>
  <div class="student-progress">
    <div class="page-header">
      <h2>学习进步分析</h2>
      <p>追踪学习进度，分析成长轨迹</p>
    </div>

    <Card class="filter-card">
      <div class="filter-section">
        <template v-if="!isStudentMode">
          <span class="filter-label">选择学生：</span>
          <Select
            v-model="selectedStudent"
            filterable
            placeholder="请选择学生"
            style="width: 250px;"
          >
            <Option
              v-for="student in students"
              :key="student.id"
              :value="student.id"
              :label="student.name"
            >
              {{ student.name }} ({{ student.userName }})
            </Option>
          </Select>
        </template>
        <template v-else>
          <span class="filter-label">当前学生：</span>
          <Tag color="blue">{{ currentStudentName || '我' }}</Tag>
        </template>

        <span class="filter-label" style="margin-left: 20px;">时间范围：</span>
        <Select v-model="timeRange" style="width: 150px;">
          <Option value="week">最近一周</Option>
          <Option value="month">最近一月</Option>
          <Option value="semester">本学期</Option>
          <Option value="year">最近一年</Option>
        </Select>

        <Button
          type="primary"
          @click="loadProgress"
          :loading="loading"
          style="margin-left: 20px;"
        >
          <Icon type="md-trending-up" />
          查看分析
        </Button>
      </div>
    </Card>

    <div v-if="progressData.length > 0">
      <Row :gutter="16">
        <Col span="6">
          <Card class="summary-card">
            <Statistic
              title="总记录数"
              :value="summary.totalRecords"
              suffix="次"
            >
              <template #prefix>
                <Icon type="md-list" style="color: #2d8cf0" />
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col span="6">
          <Card class="summary-card">
            <Statistic
              title="平均分"
              :value="summary.avgScore"
              :precision="1"
              suffix="分"
            >
              <template #prefix>
                <Icon type="md-star" style="color: #f90" />
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col span="6">
          <Card class="summary-card">
            <Statistic
              title="进步分数"
              :value="summary.improvement"
              :precision="1"
              suffix="分"
              :value-style="{
                color: summary.improvement >= 0 ? '#19be6b' : '#ed4014'
              }"
            >
              <template #prefix>
                <Icon
                  :type="summary.improvement >= 0 ? 'md-trending-up' : 'md-trending-down'"
                  :style="{ color: summary.improvement >= 0 ? '#19be6b' : '#ed4014' }"
                />
              </template>
            </Statistic>
          </Card>
        </Col>
        <Col span="6">
          <Card class="summary-card">
            <Statistic
              title="进步率"
              :value="summary.improvementRate"
              :precision="1"
              suffix="%"
              :value-style="{
                color: summary.improvementRate >= 0 ? '#19be6b' : '#ed4014'
              }"
            >
              <template #prefix>
                <Icon type="md-pulse" style="color: #2d8cf0" />
              </template>
            </Statistic>
          </Card>
        </Col>
      </Row>

      <Card class="chart-card">
        <div slot="title">
          <Icon type="md-analytics" />
          成绩变化趋势
        </div>
        <div ref="trendChart" class="chart-container"></div>
      </Card>

      <Row :gutter="16">
        <Col span="12">
          <Card class="subject-card">
            <div slot="title">
              <Icon type="md-pie" />
              各科目平均分
            </div>
            <div ref="subjectChart" class="mini-chart"></div>
          </Card>
        </Col>
        <Col span="12">
          <Card class="record-card">
            <div slot="title">
              <Icon type="md-time" />
              最近记录
            </div>
            <div class="record-list">
              <div
                v-for="(record, index) in recentRecords"
                :key="index"
                class="record-item"
              >
                <div class="record-icon">
                  <Icon
                    :type="record.type === 'exam' ? 'md-document' : 'md-create'"
                    :color="record.type === 'exam' ? '#2d8cf0' : '#19be6b'"
                  />
                </div>
                <div class="record-content">
                  <div class="record-title">{{ record.name }}</div>
                  <div class="record-meta">
                    <span class="record-subject">{{ record.subject }}</span>
                    <span class="record-date">{{ record.date }}</span>
                  </div>
                </div>
                <div class="record-score" :class="getScoreClass(record.score)">
                  {{ record.score }}分
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>

    <Card v-else class="empty-card">
      <div class="empty-content">
        <Icon type="md-trending-up" size="80" color="#dcdee2" />
        <p>请选择学生查看学习进步分析</p>
      </div>
    </Card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import {
  getLoginUser,
  getPageStudents,
  getStudentProgressStats,
  getPageStudentExamLogs,
  getPracticeLogs
} from '@/api/index.js'

export default {
  name: 'StudentProgress',
  data() {
    return {
      loading: false,
      students: [],
      selectedStudent: null,
      currentStudentName: '',
      isStudentMode: false,
      timeRange: 'semester',
      progressData: [],
      summary: {
        totalRecords: 0,
        avgScore: 0,
        improvement: 0,
        improvementRate: 0
      },
      recentRecords: [],
      trendChart: null,
      subjectChart: null
    }
  },
  mounted() {
    this.initPage()
  },
  methods: {
    getToken() {
      return this.$store.state.token || sessionStorage.getItem('token') || localStorage.getItem('token') || ''
    },
    async initPage() {
      const token = this.getToken()
      if (!token) {
        this.$Message.error('登录状态已失效，请重新登录')
        return
      }

      try {
        const userResp = await getLoginUser(token)
        const user = userResp?.data || {}
        if (user.type === 2) {
          this.isStudentMode = true
          this.selectedStudent = user.id
          this.currentStudentName = user.name || user.userName || '我'
          await this.loadStudentSelfProgress()
          return
        }
      } catch (error) {
        console.error('加载登录信息失败', error)
      }

      await this.loadStudents()
    },
    async loadStudents() {
      try {
        const resp = await getPageStudents(1, 1000, '', '', '')
        if (resp.code === 0) {
          this.students = (resp.data && resp.data.data) || []
        }
      } catch (e) {
        console.error('加载学生列表失败', e)
      }
    },
    async loadProgress() {
      if (this.isStudentMode) {
        await this.loadStudentSelfProgress()
        return
      }

      if (!this.selectedStudent && this.selectedStudent !== 0) {
        this.$Message.warning('请选择学生')
        return
      }

      this.loading = true
      try {
        const resp = await getStudentProgressStats(this.selectedStudent, this.timeRange)
        if (resp.code === 0) {
          const payload = resp.data || {}
          this.progressData = payload.progressData || []
          this.summary = payload.summary || this.emptySummary()
          this.recentRecords = this.progressData.slice(-10).reverse()
          this.$nextTick(() => {
            this.renderCharts()
          })
        } else {
          this.$Message.error(resp.msg || '加载数据失败')
        }
      } catch (e) {
        console.error('加载进步数据失败', e)
        this.$Message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },
    async loadStudentSelfProgress() {
      const token = this.getToken()
      if (!token) {
        this.$Message.error('登录状态已失效，请重新登录')
        return
      }

      this.loading = true
      try {
        const [examResp, practiceResp] = await Promise.all([
          getPageStudentExamLogs(1, 200, '', this.selectedStudent || '', ''),
          getPracticeLogs(token)
        ])

        const examRows = ((examResp.data && examResp.data.data) || []).filter(item => item && Number(item.status) === 2)
        const practiceRows = Array.isArray(practiceResp.data) ? practiceResp.data : []

        const examProgress = examRows.map(item => {
          const timeText = item.createTime || item.examTime || ''
          return {
            type: 'exam',
            name: item.examName || '考试',
            subject: item.projectName || '未分类',
            score: Number(item.score || 0),
            time: timeText,
            date: String(timeText).slice(0, 10)
          }
        })

        const practiceProgress = practiceRows
          .filter(item => item && (item.status === 'completed' || Number(item.status) === 1 || Number(item.status) === 2))
          .map(item => {
            const timeText = item.submitTime || item.createTime || item.updateTime || ''
            return {
              type: 'practice',
              name: item.paperTitle || item.title || item.name || '练习',
              subject: item.projectName || item.subject || '未分类',
              score: Number(item.score || 0),
              time: timeText,
              date: String(timeText).slice(0, 10)
            }
          })

        const merged = [...examProgress, ...practiceProgress]
          .filter(item => item.time)
          .sort((left, right) => String(left.time).localeCompare(String(right.time)))

        this.progressData = merged
        this.summary = this.buildSummary(merged)
        this.recentRecords = merged.slice(-10).reverse()

        this.$nextTick(() => {
          this.renderCharts()
        })
      } catch (error) {
        console.error('加载学生个人学习分析失败', error)
        this.$Message.error('加载学习分析失败')
      } finally {
        this.loading = false
      }
    },
    emptySummary() {
      return {
        totalRecords: 0,
        avgScore: 0,
        improvement: 0,
        improvementRate: 0,
        subjectAverages: {}
      }
    },
    buildSummary(records) {
      if (!records.length) {
        return this.emptySummary()
      }

      const avgScore = Number((records.reduce((sum, item) => sum + Number(item.score || 0), 0) / records.length).toFixed(2))
      let improvement = 0
      let improvementRate = 0

      if (records.length >= 2) {
        const firstScore = Number(records[0].score || 0)
        const lastScore = Number(records[records.length - 1].score || 0)
        improvement = Number((lastScore - firstScore).toFixed(2))
        if (firstScore > 0) {
          improvementRate = Number((((lastScore - firstScore) / firstScore) * 100).toFixed(2))
        }
      }

      const subjectMap = {}
      records.forEach(item => {
        const subject = item.subject || '未分类'
        if (!subjectMap[subject]) {
          subjectMap[subject] = []
        }
        subjectMap[subject].push(Number(item.score || 0))
      })

      const subjectAverages = {}
      Object.keys(subjectMap).forEach(subject => {
        const scores = subjectMap[subject]
        const value = scores.reduce((sum, score) => sum + score, 0) / scores.length
        subjectAverages[subject] = Number(value.toFixed(2))
      })

      return {
        totalRecords: records.length,
        avgScore,
        improvement,
        improvementRate,
        subjectAverages
      }
    },
    renderCharts() {
      this.renderTrendChart()
      this.renderSubjectChart()
    },
    renderTrendChart() {
      if (!this.$refs.trendChart) return

      if (this.trendChart) {
        this.trendChart.dispose()
      }

      this.trendChart = echarts.init(this.$refs.trendChart)

      const examData = this.progressData.filter(d => d.type === 'exam')
      const practiceData = this.progressData.filter(d => d.type === 'practice')

      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['考试成绩', '练习成绩']
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
          data: this.progressData.map(d => d.date)
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: 0,
          max: 100
        },
        series: [
          {
            name: '考试成绩',
            type: 'line',
            data: this.progressData.map(d => d.type === 'exam' ? d.score : null),
            smooth: true,
            itemStyle: { color: '#2d8cf0' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(45, 140, 240, 0.3)' },
                { offset: 1, color: 'rgba(45, 140, 240, 0.05)' }
              ])
            }
          },
          {
            name: '练习成绩',
            type: 'line',
            data: this.progressData.map(d => d.type === 'practice' ? d.score : null),
            smooth: true,
            itemStyle: { color: '#19be6b' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(25, 190, 107, 0.3)' },
                { offset: 1, color: 'rgba(25, 190, 107, 0.05)' }
              ])
            }
          }
        ]
      }

      this.trendChart.setOption(option)
    },
    renderSubjectChart() {
      if (!this.$refs.subjectChart) return

      if (this.subjectChart) {
        this.subjectChart.dispose()
      }

      this.subjectChart = echarts.init(this.$refs.subjectChart)

      const subjectData = this.summary.subjectAverages || {}
      const data = Object.entries(subjectData).map(([name, value]) => ({
        name,
        value
      }))

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}分'
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: '{b}\n{c}分'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              }
            },
            data: data
          }
        ]
      }

      this.subjectChart.setOption(option)
    },
    getScoreClass(score) {
      if (score >= 90) return 'score-excellent'
      if (score >= 80) return 'score-good'
      if (score >= 60) return 'score-pass'
      return 'score-fail'
    }
  }
}
</script>

<style scoped>
.student-progress {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.filter-card {
  margin-bottom: 24px;
}

.filter-section {
  padding: 10px 0;
  display: flex;
  align-items: center;
}

.filter-label {
  font-weight: 500;
  color: #515a6e;
}

.summary-card {
  margin-bottom: 24px;
}

.chart-card,
.subject-card,
.record-card {
  margin-bottom: 24px;
}

.chart-container {
  height: 350px;
}

.mini-chart {
  height: 250px;
}

.record-list {
  max-height: 300px;
  overflow-y: auto;
}

.record-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e8eaec;
  transition: background 0.3s;
}

.record-item:hover {
  background: #f8f8f9;
}

.record-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f5f7f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.record-content {
  flex: 1;
}

.record-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.record-meta {
  font-size: 12px;
  color: #808695;
}

.record-subject {
  margin-right: 12px;
}

.record-score {
  font-size: 18px;
  font-weight: 600;
}

.score-excellent {
  color: #19be6b;
}

.score-good {
  color: #2d8cf0;
}

.score-pass {
  color: #ff9900;
}

.score-fail {
  color: #ed4014;
}

.empty-card {
  text-align: center;
  padding: 60px 0;
}

.empty-content {
  color: #c5c8ce;
}

.empty-content p {
  margin-top: 20px;
  font-size: 16px;
}
</style>
