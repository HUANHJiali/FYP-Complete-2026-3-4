<template>
  <Card class="radar-chart-card">
    <div slot="title">
      <Icon type="ios-pulse" style="margin-right: 8px"/>
      学科能力雷达图
    </div>
    <div v-if="loading" class="loading-container">
      <Spin size="large">
        <Icon type="ios-loading" size="18" class="spin-icon-load"></Icon>
        <div class="spin-text">加载中...</div>
      </Spin>
    </div>
    <div v-else-if="chartData && chartData.length > 0" class="chart-container">
      <div ref="radarChart" style="width: 100%; height: 500px"></div>
    </div>
    <div v-else class="empty-container">
      <Icon type="ios-document-outline" size="48" color="#ccc" />
      <p>暂无数据</p>
    </div>
  </Card>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'RadarChart',
  data() {
    return {
      loading: false,
      chartData: [],
      chartInstance: null
    }
  },
  mounted() {
    this.loadChartData()
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.dispose()
      this.chartInstance = null
    }
  },
  methods: {
    async loadChartData() {
      try {
        this.loading = true
        const token = this.$store.state.token || sessionStorage.getItem('token')

        // 获取学生的考试和练习数据
        const { getStudentExams } = await import('@/api/index.js')
        const response = await getStudentExams(token)

        if (response.code === 0) {
          this.processChartData(response.data || response)
        } else {
          this.$Message.error(response.msg || '加载数据失败')
        }
      } catch (error) {
        console.error('加载雷达图数据失败:', error)
        this.$Message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },

    processChartData(data) {
      // 按学科聚合数据
      const subjectStats = {}

      // 处理考试数据
      const exams = Array.isArray(data) ? data : (data.list || data.exams || [])
      exams.forEach(exam => {
        const subject = exam.projectName || exam.project || '未知学科'
        if (!subjectStats[subject]) {
          subjectStats[subject] = {
            totalScore: 0,
            count: 0,
            maxScore: 0
          }
        }
        if (exam.score !== undefined && exam.score !== null) {
          subjectStats[subject].totalScore += exam.score
          subjectStats[subject].count += 1
          subjectStats[subject].maxScore = Math.max(subjectStats[subject].maxScore, exam.score)
        }
      })

      // 转换为雷达图数据
      const indicators = []
      const values = []

      Object.keys(subjectStats).forEach(subject => {
        const stats = subjectStats[subject]
        const avgScore = stats.count > 0 ? (stats.totalScore / stats.count).toFixed(1) : 0
        indicators.push({
          name: subject,
          max: 100 // 假设满分为100
        })
        values.push(parseFloat(avgScore))
      })

      if (indicators.length === 0) {
        // 如果没有数据，显示默认数据
        indicators.push(
          { name: '数学', max: 100 },
          { name: '语文', max: 100 },
          { name: '英语', max: 100 },
          { name: '物理', max: 100 },
          { name: '化学', max: 100 }
        )
        values.push(0, 0, 0, 0, 0)
      }

      this.chartData = { indicators, values }
      this.$nextTick(() => {
        this.initChart()
      })
    },

    initChart() {
      if (!this.$refs.radarChart || !this.chartData) {
        return
      }

      // 销毁旧实例
      if (this.chartInstance) {
        this.chartInstance.dispose()
      }

      // 创建新实例
      this.chartInstance = echarts.init(this.$refs.radarChart)

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}'
        },
        legend: {
          data: ['学科能力'],
          bottom: 10
        },
        radar: {
          indicator: this.chartData.indicators,
          radius: '65%',
          axisName: {
            color: '#1890ff',
            fontSize: 14,
            fontWeight: 'bold'
          },
          splitArea: {
            areaStyle: {
              color: ['rgba(24, 144, 255, 0.05)', 'rgba(24, 144, 255, 0.1)']
            }
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(24, 144, 255, 0.3)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(24, 144, 255, 0.3)',
              type: 'dashed'
            }
          }
        },
        series: [
          {
            name: '学科能力',
            type: 'radar',
            data: [
              {
                value: this.chartData.values,
                name: '我的能力',
                itemStyle: {
                  color: '#1890ff'
                },
                areaStyle: {
                  color: 'rgba(24, 144, 255, 0.3)'
                },
                lineStyle: {
                  color: '#1890ff',
                  width: 2
                }
              }
            ],
            symbol: 'circle',
            symbolSize: 6
          }
        ]
      }

      this.chartInstance.setOption(option)

      // 响应式调整
      window.addEventListener('resize', this.handleResize)
    },

    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    }
  }
}
</script>

<style scoped>
.radar-chart-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
  border: 1px solid rgba(24, 144, 255, 0.1);
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.spin-icon-load {
  animation: ani-demo-spin 1s linear infinite;
}

@keyframes ani-demo-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin-text {
  margin-top: 10px;
  color: #1890ff;
  font-weight: 500;
}

.empty-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
  color: #8c8c8c;
  background: #fafafa;
  border-radius: 8px;
  border: 2px dashed rgba(24, 144, 255, 0.2);
  padding: 40px;
}

.empty-container p {
  margin-top: 10px;
}

.chart-container {
  padding: 20px 0;
}
</style>
