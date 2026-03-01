export function getEmptyAdminToday() {
  return {
    todayNewQuestions: 0,
    todayNewPractices: 0,
    todayNewExams: 0
  }
}

export function getEmptyAdminTrend() {
  return {
    activeUsers7d: 0,
    passRate7d: 0,
    avgScore7d: 0
  }
}

export function getEmptyAdminReview() {
  return {
    pendingReviews: 0
  }
}

export function createWelcomeChartInstances() {
  return {
    chartQuestions: null,
    chartActive: null,
    chartDone: null,
    chartTeacherStatus: null,
    chartTeacherProject: null,
    chartStudentExam: null,
    chartStudentTask: null
  }
}
