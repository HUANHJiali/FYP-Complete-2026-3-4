<template>
  <div class="class-comparison">
    <div class="page-header">
      <h2>班级成绩对比分析</h2>
      <p>比较不同班级的考试成绩、练习表现和错题情况</p>
    </div>

    <Card class="filter-card">
      <div class="filter-section">
        <div class="filter-row">
          <span class="filter-label">选择班级：</span>
          <Select
            v-model="selectedGrades"
            multiple
            filterable
            placeholder="请选择要对比的班级"
            style="width: 400px;"
            :max-tag-count="5"
          >
            <Option
              v-for="grade in grades"
              :key="grade.id"
              :value="grade.id"
              :label="grade.name"
            >
              {{ grade.name }}
            </Option>
          </Select>
          
          <span class="filter-label" style="margin-left: 20px;">考试：</span>
          <Select
            v-model="selectedExam"
            placeholder="全部考试"
            clearable
            style="width: 200px;"
          >
            <Option
              v-for="exam in exams"
              :key="exam.id"
              :value="exam.id"
              :label="exam.name"
            >
              {{ exam.name }}
            </Option>
          </Select>

          <Button
            type="primary"
            @click="loadComparison"
            :loading="loading"
            style="margin-left: 20px;"
          >
            <Icon type="md-analytics" />
            开始对比
          </Button>
        </div>
      </div>
    </Card>

    <div v-if="comparisonData.length > 0">
      <Card class="chart-card">
        <div slot="title">
          <Icon type="md-bar-chart" />
          成绩对比图表
        </div>
        <div ref="chartContainer" class="chart-container"></div>
      </Card>

      <Card class="table-card">
        <div slot="title">
          <Icon type="md-list" />
          详细数据对比
        </div>
        <Table
          :columns="tableColumns"
          :data="comparisonData"
          border
          stripe
        >
          <template #rank="{ row }">
            <span :class="'rank rank-' + row.rank">
              <Icon v-if="row.rank === 1" type="md-trophy" class="gold" />
              <Icon v-else-if="row.rank === 2" type="md-medal" class="silver" />
              <Icon v-else-if="row.rank === 3" type="md-medal" class="bronze" />
              {{ row.rank }}
            </span>
          </template>
          <template #avgScore="{ row }">
            <span :class="getScoreClass(row.examStats.avgScore)">
              {{ row.examStats.avgScore }}
            </span>
          </template>
          <template #passRate="{ row }">
            <Progress
              :percent="row.examStats.passRate"
              :stroke-color="getProgressColor(row.examStats.passRate)"
            />
          </template>
          <template #excellentRate="{ row }">
            <Progress
              :percent="row.examStats.excellentRate"
              :stroke-color="getProgressColor(row.examStats.excellentRate)"
            />
          </template>
        </Table>
      </Card>

      <Row :gutter="16">
        <Col span="12">
          <Card class="stat-card">
            <div slot="title">
              <Icon type="md-school" />
              练习情况对比
            </div>
            <div ref="practiceChart" class="mini-chart"></div>
          </Card>
        </Col>
        <Col span="12">
          <Card class="stat-card">
            <div slot="title">
              <Icon type="md-warning" />
              错题情况对比
            </div>
            <div ref="wrongChart" class="mini-chart"></div>
          </Card>
        </Col>
      </Row>
    </div>

    <Card v-else class="empty-card">
      <div class="empty-content">
        <Icon type="md-analytics" size="80" color="#dcdee2" />
        <p>请选择至少两个班级进行对比分析</p>
      </div>
    </Card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getAllGrades, getExams } from '@/api'

export default {
  name: 'ClassComparison',
  data() {
    return {
      loading: false,
      grades: [],
      exams: [],
      selectedGrades: [],
      selectedExam: null,
      comparisonData: [],
      tableColumns: [
        {
          title: '排名',
          slot: 'rank',
          width: 80,
          align: 'center'
        },
        {
          title: '班级名称',
          key: 'gradeName',
          width: 150
        },
        {
          title: '学生人数',
          key: 'studentCount',
          width: 100,
          align: 'center'
        },
        {
          title: '平均分',
          slot: 'avgScore',
          width: 100,
          align: 'center',
          sortable: true
        },
        {
          title: '最高分',
          key: 'examStats.maxScore',
          width: 90,
          align: 'center'
        },
        {
          title: '最低分',
          key: 'examStats.minScore',
          width: 90,
          align: 'center'
        },
        {
          title: '及格率',
          slot: 'passRate',
          width: 150,
          align: 'center'
        },
        {
          title: '优秀率',
          slot: 'excellentRate',
          width: 150,
          align: 'center'
        },
        {
          title: '平均错题数',
          key: 'wrongQuestionStats.avgPerStudent',
          width: 120,
          align: 'center'
        }
      ],
      mainChart: null,
      practiceChart: null,
      wrongChart: null
    }
  },
  mounted() {
    this.loadGrades()
    this.loadExams()
  },
  methods: {
    async loadGrades() {
      try {
        const resp = await getAllGrades()
        if (resp.code === 0) {
          this.grades = resp.data
        }
      } catch (e) {
        console.error('加载班级失败', e)
      }
    },
    async loadExams() {
      try {
        const resp = await getExams({ pageIndex: 1, pageSize: 100 })
        if (resp.code === 0) {
          this.exams = resp.data.data || []
        }
      } catch (e) {
        console.error('加载考试失败', e)
      }
    },
    async loadComparison() {
      if (this.selectedGrades.length < 2) {
        this.$Message.warning('请至少选择两个班级')
        return
      }

      this.loading = true
      try {
        const gradeIds = this.selectedGrades.join(',')
        let url = `/api/statistics/compare_classes/?gradeIds=${gradeIds}`
        if (this.selectedExam) {
          url += `&examId=${this.selectedExam}`
        }

        const resp = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await resp.json()

        if (data.code === 0) {
          this.comparisonData = data.data.comparisonData
          this.$nextTick(() => {
            this.renderCharts()
          })
        } else {
          this.$Message.error(data.msg || '加载对比数据失败')
        }
      } catch (e) {
        console.error('加载对比数据失败', e)
        this.$Message.error('加载对比数据失败')
      } finally {
        this.loading = false
      }
    },
    renderCharts() {
      this.renderMainChart()
      this.renderPracticeChart()
      this.renderWrongChart()
    },
    renderMainChart() {
      if (!this.$refs.chartContainer) return

      if (this.mainChart) {
        this.mainChart.dispose()
      }

      this.mainChart = echarts.init(this.$refs.chartContainer)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['平均分', '最高分', '最低分']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.comparisonData.map(d => d.gradeName)
        },
        yAxis: {
          type: 'value',
          name: '分数'
        },
        series: [
          {
            name: '平均分',
            type: 'bar',
            data: this.comparisonData.map(d => d.examStats.avgScore),
            itemStyle: {
              color: '#2d8cf0'
            }
          },
          {
            name: '最高分',
            type: 'bar',
            data: this.comparisonData.map(d => d.examStats.maxScore),
            itemStyle: {
              color: '#19be6b'
            }
          },
          {
            name: '最低分',
            type: 'bar',
            data: this.comparisonData.map(d => d.examStats.minScore),
            itemStyle: {
              color: '#ff9900'
            }
          }
        ]
      }

      this.mainChart.setOption(option)
    },
    renderPracticeChart() {
      if (!this.$refs.practiceChart) return

      if (this.practiceChart) {
        this.practiceChart.dispose()
      }

      this.practiceChart = echarts.init(this.$refs.practiceChart)

      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '练习次数',
            type: 'pie',
            radius: '50%',
            data: this.comparisonData.map(d => ({
              value: d.practiceStats.totalPractices,
              name: d.gradeName
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }

      this.practiceChart.setOption(option)
    },
    renderWrongChart() {
      if (!this.$refs.wrongChart) return

      if (this.wrongChart) {
        this.wrongChart.dispose()
      }

      this.wrongChart = echarts.init(this.$refs.wrongChart)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.comparisonData.map(d => d.gradeName),
          axisLabel: {
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: '平均错题数'
        },
        series: [
          {
            name: '人均错题数',
            type: 'bar',
            data: this.comparisonData.map(d => d.wrongQuestionStats.avgPerStudent),
            itemStyle: {
              color: '#ed4014'
            }
          }
        ]
      }

      this.wrongChart.setOption(option)
    },
    getScoreClass(score) {
      if (score >= 90) return 'score-excellent'
      if (score >= 80) return 'score-good'
      if (score >= 60) return 'score-pass'
      return 'score-fail'
    },
    getProgressColor(percent) {
      if (percent >= 80) return '#19be6b'
      if (percent >= 60) return '#2d8cf0'
      if (percent >= 40) return '#ff9900'
      return '#ed4014'
    }
  }
}
</script>

<style scoped>
.class-comparison {
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

.page-header p {
  color: #515a6e;
}

.filter-card {
  margin-bottom: 24px;
}

.filter-section {
  padding: 10px 0;
}

.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-label {
  font-weight: 500;
  color: #515a6e;
}

.chart-card,
.table-card,
.stat-card {
  margin-bottom: 24px;
}

.chart-container {
  height: 400px;
}

.mini-chart {
  height: 300px;
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

.rank {
  font-weight: 600;
}

.rank-1 {
  color: #f90;
}

.rank-2 {
  color: #c0c0c0;
}

.rank-3 {
  color: #cd7f32;
}

.gold {
  color: gold;
}

.silver {
  color: silver;
}

.bronze {
  color: #cd7f32;
}

.score-excellent {
  color: #19be6b;
  font-weight: 600;
}

.score-good {
  color: #2d8cf0;
  font-weight: 500;
}

.score-pass {
  color: #ff9900;
}

.score-fail {
  color: #ed4014;
  font-weight: 500;
}
</style>
