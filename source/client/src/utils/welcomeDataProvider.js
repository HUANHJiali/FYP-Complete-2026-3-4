import {
  getLoginUser,
  getPageTeacherExamLogs,
  getStudentExams,
  getStudentPracticePapers,
  getStudentTasks,
  getAdminDashboardCards,
  getAdminTrends
} from '../api/index.js'
import {
  buildTeacherDashboard,
  buildStudentDashboard,
  getEmptyTeacherStats,
  getEmptyStudentStats
} from './welcomeDashboard'

export async function resolveWelcomeRole(token) {
  if (!token) {
    return {
      roleType: null,
      isAdmin: false
    }
  }

  const resp = await getLoginUser(token)
  const roleType = resp && resp.code === 0 && resp.data ? Number(resp.data.type) : null
  return {
    roleType,
    isAdmin: roleType === 0
  }
}

export async function fetchAdminDashboardBundle() {
  const [cardsResp, trendsResp] = await Promise.all([
    getAdminDashboardCards(),
    getAdminTrends()
  ])

  const cardsData = cardsResp && cardsResp.code === 0 ? (cardsResp.data || {}) : {}
  const trendsData = trendsResp && trendsResp.code === 0 ? (trendsResp.data || {}) : {}

  return {
    cardsData,
    trendsData
  }
}

export async function fetchTeacherDashboardBundle(token) {
  try {
    const resp = await getPageTeacherExamLogs(1, 200, '', token, '', '')
    const page = resp && resp.data ? resp.data : {}
    const logs = page.data || []
    return buildTeacherDashboard(logs)
  } catch (e) {
    return {
      stats: getEmptyTeacherStats(),
      chart: buildTeacherDashboard([]).chart
    }
  }
}

export async function fetchStudentDashboardBundle(token) {
  try {
    const [examsResp, papersResp, tasksResp] = await Promise.all([
      getStudentExams(token, 1, 200),
      getStudentPracticePapers(token),
      getStudentTasks(token)
    ])

    const examPage = examsResp && examsResp.data ? examsResp.data : {}
    const exams = examPage.data || []
    const papers = papersResp && papersResp.code === 0 && Array.isArray(papersResp.data) ? papersResp.data : []
    const tasks = tasksResp && tasksResp.code === 0 && Array.isArray(tasksResp.data) ? tasksResp.data : []

    return buildStudentDashboard(exams, papers, tasks)
  } catch (e) {
    return {
      stats: getEmptyStudentStats(),
      chart: buildStudentDashboard([], [], []).chart
    }
  }
}
