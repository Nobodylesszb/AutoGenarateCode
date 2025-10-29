<template>
  <div class="container">
    <div class="card" style="max-width:520px;margin:0 auto">
      <h2 class="mb-2">管理员登录</h2>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input v-model="username" class="form-input" placeholder="admin" required />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input v-model="password" type="password" class="form-input" placeholder="••••••" required />
        </div>

        <div class="mt-2">
          <button class="btn" :disabled="loading" style="width:100%">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
    </div>
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
