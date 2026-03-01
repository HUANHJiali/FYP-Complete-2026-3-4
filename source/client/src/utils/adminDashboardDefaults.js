export function createEmptyAdminDashboardData() {
  return {
    overview: {},
    monthly: {},
    activity: {},
    today: {},
    trends_7d: {
      days: [],
      practices: [],
      tasks: []
    }
  }
}

export function createAdminDashboardChartInstances() {
  return {
    trendsChart: null
  }
}
