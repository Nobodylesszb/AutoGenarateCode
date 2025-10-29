import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Purchase from '@/views/Purchase.vue'
import Activation from '@/views/Activation.vue'
import PaymentSuccess from '@/views/PaymentSuccess.vue'
import PaymentAdmin from '@/views/PaymentAdmin.vue'
import Admin from '@/views/Admin.vue'
import Login from '@/views/Login.vue'
import SimpleLogin from '@/views/SimpleLogin.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/purchase',
    name: 'Purchase',
    component: Purchase
  },
  {
    path: '/activation',
    name: 'Activation',
    component: Activation
  },
  {
    path: '/payment/success',
    name: 'PaymentSuccess',
    component: PaymentSuccess
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/auth',
    name: 'SimpleLogin',
    component: SimpleLogin
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/payments',
    name: 'PaymentAdmin',
    component: PaymentAdmin,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 临时关闭前端路由鉴权用于排查登录问题
router.beforeEach((to, from, next) => {
  next()
})

export default router
