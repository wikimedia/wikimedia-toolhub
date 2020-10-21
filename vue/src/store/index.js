import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
      user: {
        is_authenticated: false,
      }
  },
  mutations: {
      user (state, user) {
          state.user = user
      }
  },
  actions: {
      getUserInfo(context) {
        console.log("store.index.actions.getUserInfo() called");
        fetch('/user/info/', {credentials: 'same-origin'})
          .then(response => response.json())
          .then(data =>(context.commit('user', data.user)));
      }
  },
  modules: {
  },
  // Strict mode in development/testing, but disabled for performance in prod
  strict: process.env.NODE_ENV !== 'production'
})
