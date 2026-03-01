export function setChartInstance(instances, key, element, echarts, option) {
  const previous = instances[key]
  if (previous) {
    previous.dispose()
    instances[key] = null
  }

  if (!element) {
    return null
  }

  const chart = echarts.init(element)
  chart.setOption(option)
  instances[key] = chart
  return chart
}

export function disposeChartInstance(instances, key) {
  const chart = instances[key]
  if (!chart) {
    return
  }
  chart.dispose()
  instances[key] = null
}

export function disposeAllChartInstances(instances) {
  Object.keys(instances).forEach((key) => disposeChartInstance(instances, key))
}
