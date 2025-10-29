<template>
  <div class="activation">
    <div class="container">
      <div class="card">
        <h2>激活码验证</h2>
        
        <form @submit.prevent="handleActivation" class="activation-form">
          <div class="form-group">
            <label class="form-label">激活码</label>
            <input 
              type="text" 
              v-model="activationCode" 
              class="form-input"
              placeholder="请输入激活码"
              required
            >
          </div>
          
          <div class="form-group">
            <label class="form-label">用户ID (可选)</label>
            <input 
              type="text" 
              v-model="userId" 
              class="form-input"
              placeholder="请输入用户ID"
            >
          </div>
          
          <button type="submit" class="btn" :disabled="!activationCode || isProcessing">
            {{ isProcessing ? '验证中...' : '验证激活码' }}
          </button>
        </form>
        
        <div v-if="verificationResult" class="verification-result">
          <div v-if="verificationResult.valid" class="alert alert-success">
            <h3>✅ 激活码有效</h3>
            <div class="activation-details">
              <p><strong>激活码:</strong> {{ verificationResult.activation_code.code }}</p>
              <p><strong>产品:</strong> {{ verificationResult.activation_code.product_name }}</p>
              <p><strong>状态:</strong> {{ getStatusText(verificationResult.activation_code.status) }}</p>
              <p><strong>价格:</strong> ¥{{ verificationResult.activation_code.price }}</p>
              <p><strong>创建时间:</strong> {{ formatDate(verificationResult.activation_code.created_at) }}</p>
              <p v-if="verificationResult.activation_code.expires_at">
                <strong>过期时间:</strong> {{ formatDate(verificationResult.activation_code.expires_at) }}
              </p>
            </div>
            
            <div v-if="verificationResult.activation_code.status === 'unused'" class="activation-actions">
              <button @click="useActivationCode" class="btn btn-success" :disabled="isUsing">
                {{ isUsing ? '激活中...' : '立即激活' }}
              </button>
            </div>
          </div>
          
          <div v-else class="alert alert-error">
            <h3>❌ 激活码无效</h3>
            <p>{{ verificationResult.message }}</p>
          </div>
        </div>
        
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>
        
        <div v-if="success" class="alert alert-success">
          <h3>🎉 激活成功</h3>
          <p>激活码已成功激活，您现在可以使用相关服务了。</p>
        </div>
      </div>
      
      <div class="help-section">
        <h3>使用说明</h3>
        <div class="help-content">
          <div class="help-item">
            <h4>1. 获取激活码</h4>
            <p>通过购买页面购买激活码，支付成功后系统会自动生成激活码。</p>
          </div>
          <div class="help-item">
            <h4>2. 验证激活码</h4>
            <p>在此页面输入激活码进行验证，确认激活码的有效性。</p>
          </div>
          <div class="help-item">
            <h4>3. 激活使用</h4>
            <p>验证通过后点击"立即激活"按钮完成激活，激活后即可使用相关服务。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { api } from '../api/api'

export default {
  name: 'Activation',
  setup() {
    const activationCode = ref('')
    const userId = ref('')
    const verificationResult = ref(null)
    const error = ref('')
    const success = ref(false)
    const isProcessing = ref(false)
    const isUsing = ref(false)
    
    const getStatusText = (status) => {
      const statusMap = {
        'unused': '未使用',
        'used': '已使用',
        'expired': '已过期',
        'disabled': '已禁用'
      }
      return statusMap[status] || status
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    const handleActivation = async () => {
      if (!activationCode.value) return
      
      isProcessing.value = true
      error.value = ''
      verificationResult.value = null
      
      try {
        // 调用后端验证激活码
        const response = await api.activation.verifyCode(activationCode.value, userId.value || null)
        verificationResult.value = response
        
      } catch (err) {
        error.value = '验证激活码失败，请重试'
        console.error('Verification error:', err)
      } finally {
        isProcessing.value = false
      }
    }
    
    const useActivationCode = async () => {
      if (!verificationResult.value?.activation_code) return
      
      isUsing.value = true
      error.value = ''
      
      try {
        // 调用后端使用激活码
        const resp = await api.activation.useCode(activationCode.value, userId.value || null)
        if (resp && resp.success) {
          success.value = true
          if (verificationResult.value?.activation_code) {
            verificationResult.value.activation_code.status = 'used'
          }
        } else {
          throw new Error(resp?.message || '激活失败')
        }
        
      } catch (err) {
        error.value = '激活失败，请重试'
        console.error('Activation error:', err)
      } finally {
        isUsing.value = false
      }
    }
    
    return {
      activationCode,
      userId,
      verificationResult,
      error,
      success,
      isProcessing,
      isUsing,
      getStatusText,
      formatDate,
      handleActivation,
      useActivationCode
    }
  }
}
</script>

<style scoped>
.activation-form {
  max-width: 500px;
  margin: 0 auto;
}

.verification-result {
  margin-top: 2rem;
}

.activation-details {
  margin-top: 1rem;
}

.activation-details p {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
}

.activation-actions {
  margin-top: 1rem;
}

.help-section {
  margin-top: 3rem;
}

.help-section h3 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.help-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.help-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.help-item h4 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

.help-item p {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .help-content {
    grid-template-columns: 1fr;
  }
}
</style>
