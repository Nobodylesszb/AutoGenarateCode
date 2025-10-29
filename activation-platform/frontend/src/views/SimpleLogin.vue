<template>
  <div style="max-width:480px;margin:40px auto;padding:24px;background:#ffffff;border-radius:12px;box-shadow:0 4px 14px rgba(0,0,0,.08);min-height: 220px;border:2px solid #e5e7eb">
    <h2 style="margin-bottom:20px;font-size:20px;color:#111827">管理员登录</h2>
    <div v-if="error" style="margin-bottom:12px;padding:10px;border-radius:6px;background:#fdecea;color:#b71c1c">{{ error }}</div>
    <form @submit.prevent="onSubmit">
      <div style="margin-bottom:12px">
        <label style="display:block;margin-bottom:6px;color:#374151">用户名</label>
        <input v-model="username" placeholder="admin" required style="width:100%;padding:12px 14px;border:2px solid #d1d5db;border-radius:8px;font-size:16px" />
      </div>
      <div style="margin-bottom:16px">
        <label style="display:block;margin-bottom:6px;color:#374151">密码</label>
        <input v-model="password" type="password" placeholder="••••••" required style="width:100%;padding:12px 14px;border:2px solid #d1d5db;border-radius:8px;font-size:16px" />
      </div>
      <button :disabled="loading" style="width:100%;padding:14px;border:none;border-radius:8px;background:#4f46e5;color:#fff;cursor:pointer;font-size:16px">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
  </div>
  
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api/api'

const router = useRouter()
const route = useRoute()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const onSubmit = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.auth.login(username.value, password.value)
    if (res?.access_token) {
      localStorage.setItem('auth_token', res.access_token)
      const redirect = route.query.redirect || '/admin'
      router.push(String(redirect))
    } else {
      error.value = '登录失败'
    }
  } catch (e) {
    error.value = '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>


