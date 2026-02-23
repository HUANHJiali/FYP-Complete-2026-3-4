<template>
  <ChartCard
    title="成绩趋势"
    icon="ios-stats"
    :height="300"
    :chart-option="chartOption"
    :chart-types="chartTypes"
    :loading="loading"
    :error="error"
    :show-refresh="true"
    @type-change="handleTypeChange"
    @refresh="loadData" />
</template>

<script>
import ChartCard from './ChartCard.vue'
import { getPageStudentExamLogs, getPracticeLogs, getTaskLogs } from '@/api/index.js'

export default {
  name: 'ScoreTrendChart',
  components: {
    ChartCard
  },
  data() {
    return {
      loading: false,
      error: null,
      chartType: 'line',
      scoreData: [],
      chartTypes: [
        { label: '折线图', value: 'line' },
        { label: '柱状图', value: 'bar' },
        { label: '面积图', value: 'area' }
      ]
    }
  },
  computed: {
    chartOption() {
      if (!this.scoreData || this.scoreData.length === 0) {
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

      const dates = this.scoreData.map(item => item.date)
      const scores = this.scoreData.map(item => item.score)

      const baseOption = {
        title: {
          text: '成绩趋势分析',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 600
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0]
            return `${param.axisValue}<br/>${param.seriesName}: ${param.value}分`
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
          data: dates,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '分数',
          axisLabel: {
            formatter: '{value}分'
          },
          min: 0,
          max: 100
        },
        series: []
      }

      if (this.chartType === 'line') {
        baseOption.series = [{
          name: '成绩',
          type: 'line',
          data: scores,
          smooth: true,
          itemStyle: {
            color: '#667eea'
          },
          lineStyle: {
            width: 3
          },
          markPoint: {
            data: [
              { type: 'max', name: '最高分' },
              { type: 'min', name: '最低分' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均分' }
            ]
          }
        }]
      } else if (this.chartType === 'bar') {
        baseOption.series = [{
          name: '成绩',
          type: 'bar',
          data: scores,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#667eea' },
                { offset: 1, color: '#764ba2' }
              ]
            }
          }
        }]
      } else if (this.chartType === 'area') {
        baseOption.series = [{
          name: '成绩',
          type: 'line',
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
                { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
                { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
              ]
            }
          }
        }]
      }

      return baseOption
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    handleTypeChange(type) {
      this.chartType = type
    },
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        const token = this.$store.state.token || sessionStorage.getItem('token')
        const scoreMap = new Map()
        
        // 获取考试记录
        try {
          const examResponse = await getPageStudentExamLogs(1, 50, '', '', '')
          if (examResponse.code === 0 && examResponse.data && examResponse.data.list) {
            examResponse.data.list.forEach(log => {
              const date = (log.createTime || '').substring(0, 10)
              if (date && log.score !== undefined && log.score !== null) {
                if (!scoreMap.has(date)) {
                  scoreMap.set(date, [])
                }
                scoreMap.get(date).push(log.score)
              }
            })
          }
        } catch (error) {
          console.error('加载考试记录失败:', error)
        }
        
        // 获取练习记录
        try {
          const practiceResponse = await getPracticeLogs(token)
          if (practiceResponse.code === 0 && practiceResponse.data) {
            practiceResponse.data.forEach(log => {
              const date = (log.endTime || log.startTime || '').substring(0, 10)
              if (date && log.score !== undefined && log.score !== null) {
                if (!scoreMap.has(date)) {
                  scoreMap.set(date, [])
                }
                scoreMap.get(date).push(log.score)
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
              if (date && log.score !== undefined && log.score !== null) {
                if (!scoreMap.has(date)) {
                  scoreMap.set(date, [])
                }
                scoreMap.get(date).push(log.score)
              }
            })
          }
        } catch (error) {
          console.error('加载任务记录失败:', error)
        }
        
        // 转换为数组并计算平均分
        this.scoreData = Array.from(scoreMap.entries())
          .map(([date, scores]) => ({
            date,
            score: scores.length > 0 
              ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1)
              : 0
          }))
          .sort((a, b) => a.date.localeCompare(b.date))
          .slice(-30) // 只显示最近30天
        
      } catch (error) {
        console.error('加载成绩趋势失败:', error)
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

