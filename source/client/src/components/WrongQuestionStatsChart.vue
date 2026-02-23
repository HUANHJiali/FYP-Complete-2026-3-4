<template>
  <ChartCard
    title="错题统计"
    icon="ios-close-circle"
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
import { getPageWrongQuestions } from '@/api/index.js'

export default {
  name: 'WrongQuestionStatsChart',
  components: {
    ChartCard
  },
  data() {
    return {
      loading: false,
      error: null,
      chartType: 'pie',
      wrongQuestionData: [],
      chartTypes: [
        { label: '饼图', value: 'pie' },
        { label: '柱状图', value: 'bar' }
      ]
    }
  },
  computed: {
    chartOption() {
      if (!this.wrongQuestionData || this.wrongQuestionData.length === 0) {
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

      if (this.chartType === 'pie') {
        return {
          title: {
            text: '错题类型分布',
            left: 'center',
            textStyle: {
              fontSize: 16,
              fontWeight: 600
            }
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            bottom: '10%'
          },
          series: [
            {
              name: '错题类型',
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
                formatter: '{b}: {c} ({d}%)'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: 16,
                  fontWeight: 'bold'
                }
              },
              data: this.wrongQuestionData.map(item => ({
                value: item.count,
                name: item.typeName
              }))
            }
          ]
        }
      } else {
        return {
          title: {
            text: '错题类型统计',
            left: 'center',
            textStyle: {
              fontSize: 16,
              fontWeight: 600
            }
          },
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
            data: this.wrongQuestionData.map(item => item.typeName),
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '错题数量'
          },
          series: [
            {
              name: '错题数量',
              type: 'bar',
              data: this.wrongQuestionData.map(item => item.count),
              itemStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: '#ff4d4f' },
                    { offset: 1, color: '#ff7875' }
                  ]
                }
              }
            }
          ]
        }
      }
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
        const studentId = this.$store.state.userInfo?.id || null
        
        const response = await getPageWrongQuestions(1, 1000, studentId, '')
        
        if (response.code === 0 && response.data && response.data.list) {
          const typeMap = new Map()
          
          response.data.list.forEach(item => {
            const type = item.type || 0
            const typeName = this.getTypeName(type)
            
            if (!typeMap.has(typeName)) {
              typeMap.set(typeName, 0)
            }
            typeMap.set(typeName, typeMap.get(typeName) + 1)
          })
          
          this.wrongQuestionData = Array.from(typeMap.entries())
            .map(([typeName, count]) => ({
              typeName,
              count
            }))
            .sort((a, b) => b.count - a.count)
        }
      } catch (error) {
        console.error('加载错题统计失败:', error)
        this.error = '加载数据失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    getTypeName(type) {
      const typeMap = {
        0: '选择题',
        1: '填空题',
        2: '判断题',
        3: '编程题'
      }
      return typeMap[type] || '未知类型'
    }
  }
}
</script>

<style scoped>
/* 样式已由ChartCard组件提供 */
</style>

