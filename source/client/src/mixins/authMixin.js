/**
 * 认证相关混入
 * 统一处理token获取逻辑，避免在多个组件中重复
 */
export default {
  computed: {
    /**
     * 获取当前用户的token
     * 优先从Vuex store获取，如果没有则从sessionStorage获取
     * @returns {string} token字符串
     */
    token() {
      return this.$store.state.token || sessionStorage.getItem('token') || ''
    },

    /**
     * 判断用户是否已登录
     * @returns {boolean} 是否已登录
     */
    isLoggedIn() {
      return !!this.token
    }
  },

  methods: {
    /**
     * 检查登录状态
     * 如果未登录，显示提示并跳转到登录页
     * @param {string} message - 提示消息，默认为'请先登录'
     * @returns {boolean} 是否已登录
     */
    checkLogin(message = '请先登录') {
      if (!this.isLoggedIn) {
        this.$Message.error(message)
        this.$router.push('/login')
        return false
      }
      return true
    },

    /**
     * 清除登录状态
     * 清除Vuex和sessionStorage中的token
     */
    clearAuth() {
      this.$store.commit('SET_TOKEN', '')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('userInfo')
    },

    /**
     * 保存token到store和sessionStorage
     * @param {string} token - token字符串
     */
    saveToken(token) {
      this.$store.commit('SET_TOKEN', token)
      sessionStorage.setItem('token', token)
    },

    /**
     * 获取带token的请求参数
     * @param {Object} params - 原始参数对象
     * @returns {Object} 包含token的参数对象
     */
    getAuthParams(params = {}) {
      return {
        ...params,
        token: this.token
      }
    }
  }
}
