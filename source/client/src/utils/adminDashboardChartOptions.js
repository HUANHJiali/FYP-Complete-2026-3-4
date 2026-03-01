export function buildAdminDashboardTrendsOption(trends = {}) {
  return {
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
      data: trends.days || [],
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
        data: trends.practices || [],
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
        data: trends.tasks || [],
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
}
