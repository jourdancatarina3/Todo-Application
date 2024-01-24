import Vue from 'vue'
import App from './App.vue'
import router from './router'
import sileo from "sileo";

Vue.config.productionTip = false
sileo.defaults.baseUrl = "http://127.0.0.1:8000";

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
