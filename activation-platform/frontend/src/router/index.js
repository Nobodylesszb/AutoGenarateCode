import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Purchase from '@/views/Purchase.vue'
import Activation from '@/views/Activation.vue'
import PaymentSuccess from '@/views/PaymentSuccess.vue'
import PaymentAdmin from '@/views/PaymentAdmin.vue'
import Admin from '@/views/Admin.vue'

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
    path: '/admin',
    name: 'Admin',
    component: Admin
  },
  {
    path: '/admin/payments',
    name: 'PaymentAdmin',
    component: PaymentAdmin
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
