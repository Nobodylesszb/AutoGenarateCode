import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css'

// 导入页面组件
import Home from './views/Home.vue'
import Purchase from './views/Purchase.vue'
import Activation from './views/Activation.vue'
import PaymentSuccess from './views/PaymentSuccess.vue'
import PaymentAdmin from './views/PaymentAdmin.vue'
import Admin from './views/Admin.vue'

// 路由配置
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/purchase', name: 'Purchase', component: Purchase },
  { path: '/activation', name: 'Activation', component: Activation },
  { path: '/payment/success', name: 'PaymentSuccess', component: PaymentSuccess },
  { path: '/admin', name: 'Admin', component: Admin },
  { path: '/admin/payments', name: 'PaymentAdmin', component: PaymentAdmin }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 创建应用
const app = createApp(App)

// 使用插件
app.use(router)
app.use(createPinia())

// 挂载应用
app.mount('#app')
