<template>
  <div class="progress-chart">
    <Card title="成绩进步曲线" :bordered="false" style="width: 100%">
      <template #extra>
        <Select v-model="timeRange" style="width: 120px" @on-change="handleTimeRangeChange">
          <Option value="month">最近一月</Option>
          <Option value="semester">本学期</Option>
          <Option value="year">最近一年</Option>
        </Select>
      </template>
      <div ref="chartRef" style="width: 100%; height: 400px"></div>
    </Card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getExamLogs, getPracticeLogs } from '@/api'

export default {
  name: 'ProgressChart',
  props: {
    studentId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      timeRange: 'semester',
      chart: null,
      examData: [],
      practiceData: []
    }
  },
  mounted() {
    this.initChart()
    this.loadData()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose()
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartRef)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
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
          data: []
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}分'
          }
        },
        series: [
          {
            name: '考试成绩',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: {
              width: 3
            },
            itemStyle: {
              color: '#5470c6'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
                { offset: 1, color: 'rgba(84, 112, 198, 0.05)' }
              ])
            }
          },
          {
            name: '练习成绩',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: {
              width: 3,
              type: 'dashed'
            },
            itemStyle: {
              color: '#91cc75'
            }
          }
        ]
      }
      this.chart.setOption(option)
    },
    async loadData() {
      try {
        // 加载考试记录
        const examRes = await getExamLogs({
          studentId: this.studentId,
          pageSize: 100
        })
        if (examRes.code === 0) {
          this.examData = examRes.data.data || []
        }

        // 加载练习记录
        const practiceRes = await getPracticeLogs({
          studentId: this.studentId,
          pageSize: 100
        })
        if (practiceRes.code === 0) {
          this.practiceData = practiceRes.data.data || []
        }

        this.updateChart()
      } catch (error) {
        console.error('加载进度数据失败:', error)
        this.$Message.error('加载数据失败')
      }
    },
    updateChart() {
      // 合并并排序所有数据点
      const allData = []

      // 处理考试数据
      this.examData.forEach(item => {
        allData.push({
          date: item.createTime,
          score: item.score,
          type: 'exam',
          name: item.examName || '考试'
        })
      })

      // 处理练习数据
      this.practiceData.forEach(item => {
        allData.push({
          date: item.createTime,
          score: item.score || 0,
          type: 'practice',
          name: item.practiceName || '练习'
        })
      })

      // 按日期排序
      allData.sort((a, b) => new Date(a.date) - new Date(b.date))

      // 根据时间范围过滤
      const filteredData = this.filterByTimeRange(allData)

      // 提取日期和分数
      const dates = filteredData.map(d => this.formatDate(d.date))
      const examScores = []
      const practiceScores = []

      filteredData.forEach(d => {
        if (d.type === 'exam') {
          examScores.push({
            value: d.score,
            name: d.name
          })
        } else {
          practiceScores.push({
            value: d.score,
            name: d.name
          })
        }
      })

      // 更新图表
      this.chart.setOption({
        xAxis: {
          data: dates
        },
        series: [
          {
            data: examScores
          },
          {
            data: practiceScores
          }
        ]
      })
    },
    filterByTimeRange(data) {
      const now = new Date()
      let startDate

      switch (this.timeRange) {
        case 'month':
          startDate = new Date(now.setMonth(now.getMonth() - 1))
          break
        case 'semester':
          // 假设学期为5个月
          startDate = new Date(now.setMonth(now.getMonth() - 5))
          break
        case 'year':
          startDate = new Date(now.setFullYear(now.getFullYear() - 1))
          break
        default:
          return data
      }

      return data.filter(d => new Date(d.date) >= startDate)
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return `${date.getMonth() + 1}/${date.getDate()}`
    },
    handleTimeRangeChange() {
      this.updateChart()
    }
  }
}
</script>

<style scoped>
.progress-chart {
  padding: 20px;
}
</style>
