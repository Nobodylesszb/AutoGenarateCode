<template>
  <nav class="navigation">
    <div class="container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <i class="fas fa-key"></i>
          激活码平台
        </router-link>
      </div>
      
      <div class="nav-menu">
        <router-link to="/" class="nav-link">
          <i class="fas fa-home"></i>
          首页
        </router-link>
        
        <router-link to="/purchase" class="nav-link">
          <i class="fas fa-shopping-cart"></i>
          购买激活码
        </router-link>
        
        <router-link to="/activation" class="nav-link">
          <i class="fas fa-check-circle"></i>
          激活验证
        </router-link>
        
        <div class="nav-dropdown" v-if="isAuthed">
          <button class="nav-link dropdown-toggle">
            <i class="fas fa-cog"></i>
            管理后台
            <i class="fas fa-chevron-down"></i>
          </button>
          <div class="dropdown-menu">
            <router-link to="/admin" class="dropdown-item">
              <i class="fas fa-tachometer-alt"></i>
              系统概览
            </router-link>
            <router-link to="/admin/payments" class="dropdown-item">
              <i class="fas fa-credit-card"></i>
              支付管理
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="nav-auth">
        <template v-if="isAuthed">
          <button class="nav-link" @click="logout">
            <i class="fas fa-sign-out-alt"></i>
            退出
          </button>
        </template>
        <template v-else>
          <router-link to="/auth" class="nav-link">
            <i class="fas fa-user"></i>
            登录
          </router-link>
        </template>
      </div>

      <div class="nav-toggle" @click="toggleMobileMenu">
        <i class="fas fa-bars"></i>
      </div>
    </div>
    
    <!-- 移动端菜单 -->
    <div v-if="showMobileMenu" class="mobile-menu">
      <router-link to="/" class="mobile-link" @click="closeMobileMenu">
        <i class="fas fa-home"></i>
        首页
      </router-link>
      
      <router-link to="/purchase" class="mobile-link" @click="closeMobileMenu">
        <i class="fas fa-shopping-cart"></i>
        购买激活码
      </router-link>
      
      <router-link to="/activation" class="mobile-link" @click="closeMobileMenu">
        <i class="fas fa-check-circle"></i>
        激活验证
      </router-link>
      
      <div class="mobile-section" v-if="isAuthed">
        <div class="mobile-section-title">管理后台</div>
        <router-link to="/admin" class="mobile-link" @click="closeMobileMenu">
          <i class="fas fa-tachometer-alt"></i>
          系统概览
        </router-link>
        <router-link to="/admin/payments" class="mobile-link" @click="closeMobileMenu">
          <i class="fas fa-credit-card"></i>
          支付管理
        </router-link>
      </div>

      <div class="mobile-section">
        <div class="mobile-section-title">账户</div>
        <template v-if="isAuthed">
          <button class="mobile-link" @click="handleMobileLogout">
            <i class="fas fa-sign-out-alt"></i>
            退出
          </button>
        </template>
        <template v-else>
          <router-link to="/auth" class="mobile-link" @click="closeMobileMenu">
            <i class="fas fa-user"></i>
            登录
          </router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const showMobileMenu = ref(false)
const router = useRouter()

const isAuthed = computed(() => !!localStorage.getItem('auth_token'))

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const logout = () => {
  localStorage.removeItem('auth_token')
  router.push('/')
}

const handleMobileLogout = () => {
  logout()
  closeMobileMenu()
}
</script>

<style scoped>
.navigation {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.nav-brand {
  flex-shrink: 0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.2s;
}

.brand-link:hover {
  color: #2563eb;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  color: #3b82f6;
  background: #f0f9ff;
}

.nav-link.router-link-active {
  color: #3b82f6;
  background: #f0f9ff;
}

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0;
  min-width: 200px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s;
}

.nav-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
}

.dropdown-item:hover {
  color: #3b82f6;
  background: #f0f9ff;
}

.nav-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mobile-menu {
  display: none;
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 1rem;
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  color: #6b7280;
  text-decoration: none;
  border-bottom: 1px solid #f3f4f6;
  transition: color 0.2s;
}

.mobile-link:hover {
  color: #3b82f6;
}

.mobile-link.router-link-active {
  color: #3b82f6;
  font-weight: 600;
}

.mobile-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.mobile-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .nav-toggle {
    display: block;
  }
  
  .mobile-menu {
    display: block;
  }
  
  .container {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  .brand-link {
    font-size: 1rem;
  }
  
  .container {
    height: 56px;
  }
}
</style>
