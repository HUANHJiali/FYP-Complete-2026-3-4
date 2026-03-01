import { normalizeLifecycleStatus } from './lifecycleStatus'

export function getEmptyTeacherStats() {
  return {
    totalLogs: 0,
    ongoingExams: 0,
    pendingPublish: 0,
    finishedExams: 0
  }
}

export function getEmptyStudentStats() {
  return {
    availableExams: 0,
    practicePapers: 0,
    pendingTasks: 0,
    completedTasks: 0
  }
}

export function buildTeacherDashboard(logs = []) {
  const stats = {
    totalLogs: logs.length,
    ongoingExams: logs.filter(item => Number(item.status) === 0).length,
    pendingPublish: logs.filter(item => Number(item.status) === 1).length,
    finishedExams: logs.filter(item => Number(item.status) > 1).length
  }

  const projectCounter = {}
  logs.forEach(item => {
    const key = item.projectName || '未知科目'
    projectCounter[key] = (projectCounter[key] || 0) + 1
  })

  const projectNames = Object.keys(projectCounter)
  const projectValues = projectNames.map(name => projectCounter[name])

  return {
    stats,
    chart: {
      statusData: [stats.ongoingExams, stats.pendingPublish, stats.finishedExams],
      projectNames: projectNames.length ? projectNames : ['暂无数据'],
      projectValues: projectValues.length ? projectValues : [0]
    }
  }
}

export function buildStudentDashboard(exams = [], papers = [], tasks = []) {
  const pendingExamCount = exams.filter(item => {
    const lifecycle = normalizeLifecycleStatus(item)
    return lifecycle === 'not_started' || lifecycle === 'in_progress'
  }).length

  const pendingTaskCount = tasks.filter(item => {
    const lifecycle = normalizeLifecycleStatus(item)
    return lifecycle === 'not_started' || lifecycle === 'in_progress'
  }).length

  const completedTaskCount = tasks.filter(item => normalizeLifecycleStatus(item) === 'completed').length

  const stats = {
    availableExams: pendingExamCount,
    practicePapers: papers.length,
    pendingTasks: pendingTaskCount,
    completedTasks: completedTaskCount
  }

  const examLifecycleCounter = {
    not_started: 0,
    in_progress: 0,
    completed: 0,
    overdue: 0
  }
  exams.forEach(item => {
    const lifecycle = normalizeLifecycleStatus(item)
    if (examLifecycleCounter[lifecycle] !== undefined) {
      examLifecycleCounter[lifecycle] += 1
    }
  })

  const taskLifecycleCounter = {
    not_started: 0,
    in_progress: 0,
    completed: 0,
    overdue: 0
  }
  tasks.forEach(item => {
    const lifecycle = normalizeLifecycleStatus(item)
    if (taskLifecycleCounter[lifecycle] !== undefined) {
      taskLifecycleCounter[lifecycle] += 1
    }
  })

  return {
    stats,
    chart: {
      examSeries: [
        examLifecycleCounter.not_started,
        examLifecycleCounter.in_progress,
        examLifecycleCounter.completed,
        examLifecycleCounter.overdue
      ],
      taskSeries: [
        taskLifecycleCounter.not_started,
        taskLifecycleCounter.in_progress,
        taskLifecycleCounter.completed,
        taskLifecycleCounter.overdue
      ]
    }
  }
}
