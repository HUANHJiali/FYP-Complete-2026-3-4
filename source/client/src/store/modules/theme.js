/**
 * 主题状态管理模块
 */
const state = {
  currentTheme: localStorage.getItem('theme') || 'light',
  primaryColor: localStorage.getItem('primaryColor') || '#2d8cf0',
  fontSize: localStorage.getItem('fontSize') || 'medium',
  sidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true',
  showAnimations: localStorage.getItem('showAnimations') !== 'false',
  compactMode: localStorage.getItem('compactMode') === 'true'
}

const mutations = {
  SET_THEME(state, theme) {
    state.currentTheme = theme
    localStorage.setItem('theme', theme)
  },
  
  SET_PRIMARY_COLOR(state, color) {
    state.primaryColor = color
    localStorage.setItem('primaryColor', color)
  },
  
  SET_FONT_SIZE(state, size) {
    state.fontSize = size
    localStorage.setItem('fontSize', size)
  },
  
  SET_SIDEBAR_COLLAPSED(state, collapsed) {
    state.sidebarCollapsed = collapsed
    localStorage.setItem('sidebarCollapsed', collapsed)
  },
  
  SET_SHOW_ANIMATIONS(state, show) {
    state.showAnimations = show
    localStorage.setItem('showAnimations', show)
  },
  
  SET_COMPACT_MODE(state, compact) {
    state.compactMode = compact
    localStorage.setItem('compactMode', compact)
  }
}

const actions = {
  setTheme({ commit }, theme) {
    commit('SET_THEME', theme)
  },
  
  setPrimaryColor({ commit }, color) {
    commit('SET_PRIMARY_COLOR', color)
  },
  
  setFontSize({ commit }, size) {
    commit('SET_FONT_SIZE', size)
  },
  
  toggleSidebar({ commit, state }) {
    commit('SET_SIDEBAR_COLLAPSED', !state.sidebarCollapsed)
  },
  
  async loadTheme({ commit }) {
    try {
      const userId = localStorage.getItem('userId')
      if (!userId) return
      
      const resp = await fetch(`/api/theme/get/?userId=${userId}`)
      const data = await resp.json()
      
      if (data.code === 0) {
        commit('SET_THEME', data.data.theme)
        commit('SET_PRIMARY_COLOR', data.data.primaryColor)
        commit('SET_FONT_SIZE', data.data.fontSize)
        commit('SET_SIDEBAR_COLLAPSED', data.data.sidebarCollapsed)
        commit('SET_SHOW_ANIMATIONS', data.data.showAnimations)
        commit('SET_COMPACT_MODE', data.data.compactMode)
      }
    } catch (e) {
      console.error('加载主题设置失败', e)
    }
  },
  
  async saveTheme({ commit }, settings) {
    try {
      const userId = localStorage.getItem('userId')
      const formData = new FormData()
      formData.append('userId', userId)
      Object.keys(settings).forEach(key => {
        formData.append(key, settings[key])
      })
      
      const resp = await fetch('/api/theme/save/', {
        method: 'POST',
        body: formData
      })
      const data = await resp.json()
      
      if (data.code === 0) {
        commit('SET_THEME', data.data.theme)
        commit('SET_PRIMARY_COLOR', data.data.primaryColor)
        commit('SET_FONT_SIZE', data.data.fontSize)
        commit('SET_SIDEBAR_COLLAPSED', data.data.sidebarCollapsed)
        commit('SET_SHOW_ANIMATIONS', data.data.showAnimations)
        commit('SET_COMPACT_MODE', data.data.compactMode)
        return true
      }
      return false
    } catch (e) {
      console.error('保存主题设置失败', e)
      return false
    }
  },
  
  async resetTheme({ commit }) {
    try {
      const userId = localStorage.getItem('userId')
      const formData = new FormData()
      formData.append('userId', userId)
      
      const resp = await fetch('/api/theme/reset/', {
        method: 'POST',
        body: formData
      })
      const data = await resp.json()
      
      if (data.code === 0) {
        commit('SET_THEME', 'light')
        commit('SET_PRIMARY_COLOR', '#2d8cf0')
        commit('SET_FONT_SIZE', 'medium')
        commit('SET_SIDEBAR_COLLAPSED', false)
        commit('SET_SHOW_ANIMATIONS', true)
        commit('SET_COMPACT_MODE', false)
        return true
      }
      return false
    } catch (e) {
      console.error('重置主题设置失败', e)
      return false
    }
  }
}

const getters = {
  currentTheme: state => state.currentTheme,
  isDark: state => state.currentTheme === 'dark',
  primaryColor: state => state.primaryColor,
  fontSize: state => state.fontSize,
  sidebarCollapsed: state => state.sidebarCollapsed,
  showAnimations: state => state.showAnimations,
  compactMode: state => state.compactMode
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
