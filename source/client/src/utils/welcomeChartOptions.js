function baseGrid() {
  return { left: '3%', right: '4%', bottom: '3%', containLabel: true }
}

export function buildAdminQuestionsOption(data = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: data.months || [] },
    yAxis: { type: 'value' },
    series: [{ name: '题目数', type: 'bar', data: data.questionsByMonth || [], barWidth: '50%' }]
  }
}

export function buildAdminActiveOption(data = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: data.days || [], boundaryGap: false },
    yAxis: { type: 'value' },
    series: [{ name: '活跃用户', type: 'line', smooth: true, data: data.activeUsersDaily || [] }]
  }
}

export function buildAdminDoneOption(data = {}) {
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['练习完成', '任务完成'] },
    grid: baseGrid(),
    xAxis: { type: 'category', data: data.days || [] },
    yAxis: { type: 'value' },
    series: [
      { name: '练习完成', type: 'bar', stack: 'total', data: data.practiceDoneDaily || [] },
      { name: '任务完成', type: 'bar', stack: 'total', data: data.taskDoneDaily || [] }
    ]
  }
}

export function buildTeacherStatusOption(chartData = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: ['考试中', '待公布', '已完成'] },
    yAxis: { type: 'value' },
    series: [{ name: '数量', type: 'bar', data: chartData.statusData || [0, 0, 0], barWidth: '45%' }]
  }
}

export function buildTeacherProjectOption(chartData = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: chartData.projectNames || ['暂无数据'] },
    yAxis: { type: 'value' },
    series: [{ name: '考试记录数', type: 'bar', data: chartData.projectValues || [0], barWidth: '45%' }]
  }
}

export function buildStudentExamOption(chartData = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: ['未开始', '进行中', '已完成', '已逾期'] },
    yAxis: { type: 'value' },
    series: [{ name: '考试数量', type: 'bar', data: chartData.examSeries || [0, 0, 0, 0], barWidth: '45%' }]
  }
}

export function buildStudentTaskOption(chartData = {}) {
  return {
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: ['未开始', '进行中', '已完成', '已逾期'] },
    yAxis: { type: 'value' },
    series: [{ name: '任务数量', type: 'line', smooth: true, data: chartData.taskSeries || [0, 0, 0, 0] }]
  }
}
