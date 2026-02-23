import { createStore } from 'vuex'

export default createStore({
  state: {
    token: null,
	menus: null,
  },
  mutations: {
    setToken(state, newToken){
		state.token = newToken;
	},
	clearToken(state){
		state.token = null;
	},
	setMenus(state, menus){
		state.menus = menus;
	},
	clearMenus(state){
		state.menus = null;
	},
  },
  actions: {
  },
  modules: {
  }
})
