<template>
  <ChartCard
    title="学习进度"
    icon="ios-trending-up"
    :height="300"
    :chart-option="chartOption"
    :loading="loading"
    :error="error"
    :show-refresh="true"
    @refresh="loadData" />
</template>

<script>
import ChartCard from './ChartCard.vue'
import { getPracticeLogs, getTaskLogs, getPageStudentExamLogs } from '@/api/index.js'

export default {
  name: 'StudentProgressChart',
  components: {
    ChartCard
  },
  data() {
    return {
      loading: false,
      error: null,
      progressData: []
    }
  },
  computed: {
    chartOption() {
      if (!this.progressData || this.progressData.length === 0) {
        return {
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'middle',
            textStyle: {
              color: '#999'
            }
          }
        }
      }

      const dates = this.progressData.map(item => item.date)
      const scores = this.progressData.map(item => item.avgScore)
      const counts = this.progressData.map(item => item.count)

      return {
        title: {
          text: '学习进度趋势',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 600
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: (params) => {
            let result = `${params[0].axisValue}<br/>`
            params.forEach(param => {
              result += `${param.seriesName}: ${param.value}${param.seriesName.includes('分数') ? '分' : '次'}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['平均分数', '练习次数'],
          bottom: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '分数',
            position: 'left',
            axisLabel: {
              formatter: '{value}分'
            }
          },
          {
            type: 'value',
            name: '次数',
            position: 'right',
            axisLabel: {
              formatter: '{value}次'
            }
          }
        ],
        series: [
          {
            name: '平均分数',
            type: 'line',
            yAxisIndex: 0,
            data: scores,
            smooth: true,
            itemStyle: {
              color: '#667eea'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                  { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
                ]
              }
            }
          },
          {
            name: '练习次数',
            type: 'bar',
            yAxisIndex: 1,
            data: counts,
            itemStyle: {
              color: '#764ba2'
            }
          }
        ]
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        const token = this.$store.state.token || sessionStorage.getItem('token')
        const progressMap = new Map()
        
        // 获取练习记录
        try {
          const practiceResponse = await getPracticeLogs(token)
          if (practiceResponse.code === 0 && practiceResponse.data) {
            practiceResponse.data.forEach(log => {
              const date = (log.endTime || log.startTime || '').substring(0, 10)
              if (date) {
                if (!progressMap.has(date)) {
                  progressMap.set(date, { scores: [], count: 0 })
                }
                const dayData = progressMap.get(date)
                if (log.score !== undefined && log.score !== null) {
                  dayData.scores.push(log.score)
                }
                dayData.count++
              }
            })
          }
        } catch (error) {
          console.error('加载练习记录失败:', error)
        }
        
        // 获取任务记录
        try {
          const taskResponse = await getTaskLogs(token)
          if (taskResponse.code === 0 && taskResponse.data) {
            taskResponse.data.forEach(log => {
              const date = (log.endTime || log.startTime || '').substring(0, 10)
              if (date) {
                if (!progressMap.has(date)) {
                  progressMap.set(date, { scores: [], count: 0 })
                }
                const dayData = progressMap.get(date)
                if (log.score !== undefined && log.score !== null) {
                  dayData.scores.push(log.score)
                }
                dayData.count++
              }
            })
          }
        } catch (error) {
          console.error('加载任务记录失败:', error)
        }
        
        // 获取考试记录
        try {
          const examResponse = await getPageStudentExamLogs(1, 50, '', '', '')
          if (examResponse.code === 0 && examResponse.data && examResponse.data.list) {
            examResponse.data.list.forEach(log => {
              const date = (log.createTime || '').substring(0, 10)
              if (date) {
                if (!progressMap.has(date)) {
                  progressMap.set(date, { scores: [], count: 0 })
                }
                const dayData = progressMap.get(date)
                if (log.score !== undefined && log.score !== null) {
                  dayData.scores.push(log.score)
                }
                dayData.count++
              }
            })
          }
        } catch (error) {
          console.error('加载考试记录失败:', error)
        }
        
        // 转换为数组并计算平均值
        this.progressData = Array.from(progressMap.entries())
          .map(([date, data]) => ({
            date,
            avgScore: data.scores.length > 0 
              ? (data.scores.reduce((sum, score) => sum + score, 0) / data.scores.length).toFixed(1)
              : 0,
            count: data.count
          }))
          .sort((a, b) => a.date.localeCompare(b.date))
          .slice(-30) // 只显示最近30天
        
      } catch (error) {
        console.error('加载学习进度失败:', error)
        this.error = '加载数据失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* 样式已由ChartCard组件提供 */
</style>

