<template>
  <div class="payment-success">
    <div class="container">
      <div class="success-card">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        
        <h1 class="success-title">支付成功！</h1>
        
        <div v-if="paymentInfo" class="payment-details">
          <div class="detail-item">
            <span class="label">订单号：</span>
            <span class="value">{{ paymentInfo.payment_id }}</span>
          </div>
          
          <div class="detail-item">
            <span class="label">产品名称：</span>
            <span class="value">{{ paymentInfo.product_name }}</span>
          </div>
          
          <div class="detail-item">
            <span class="label">支付金额：</span>
            <span class="value">¥{{ paymentInfo.amount }}</span>
          </div>
          
          <div class="detail-item">
            <span class="label">激活码：</span>
            <span class="value activation-code">{{ paymentInfo.activation_code }}</span>
            <button @click="copyActivationCode" class="copy-btn">
              <i class="fas fa-copy"></i>
            </button>
          </div>
          
          <div class="detail-item">
            <span class="label">支付时间：</span>
            <span class="value">{{ formatDate(paymentInfo.paid_at) }}</span>
          </div>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="actions">
          <button @click="goToActivation" class="btn btn-primary">
            <i class="fas fa-key"></i>
            立即激活
          </button>
          
          <button @click="goToHome" class="btn btn-secondary">
            <i class="fas fa-home"></i>
            返回首页
          </button>
        </div>
        
        <div class="tips">
          <h3>使用说明：</h3>
          <ul>
            <li>请妥善保管您的激活码</li>
            <li>激活码仅限一次使用</li>
            <li>如有问题请联系客服</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/api'

const route = useRoute()
const router = useRouter()

const paymentId = ref(route.query.payment_id || '')
const paymentInfo = ref(null)
const error = ref('')

const fetchPaymentInfo = async () => {
  if (!paymentId.value) {
    error.value = '缺少支付ID参数'
    return
  }
  
  try {
    // 调用API获取支付成功信息
    const response = await api.payment.getPaymentSuccessInfo(paymentId.value)
    
    if (response.success) {
      paymentInfo.value = {
        payment_id: response.payment_id,
        amount: response.amount,
        product_name: response.product_name,
        activation_code: response.activation_code,
        paid_at: response.paid_at
      }
    } else {
      error.value = '获取支付信息失败'
    }
    
  } catch (error) {
    console.error('获取支付信息失败:', error)
    error.value = '获取支付信息失败'
  }
}

const copyActivationCode = async () => {
  if (paymentInfo.value?.activation_code) {
    try {
      await navigator.clipboard.writeText(paymentInfo.value.activation_code)
      alert('激活码已复制到剪贴板')
    } catch (err) {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    }
  }
}

const goToActivation = () => {
  if (paymentInfo.value?.activation_code) {
    router.push(`/activation?code=${paymentInfo.value.activation_code}`)
  } else {
    router.push('/activation')
  }
}

const goToHome = () => {
  router.push('/')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchPaymentInfo()
})
</script>

<style scoped>
.payment-success {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 1rem;
}

.success-card {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.success-icon {
  font-size: 4rem;
  color: #10b981;
  margin-bottom: 1.5rem;
}

.success-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 2rem;
}

.payment-details {
  background: #f9fafb;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: left;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.detail-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #374151;
  min-width: 100px;
}

.value {
  color: #1f2937;
  font-weight: 500;
}

.activation-code {
  font-family: 'Courier New', monospace;
  background: #1f2937;
  color: #10b981;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 1px;
}

.copy-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: background-color 0.2s;
}

.copy-btn:hover {
  background: #2563eb;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #fecaca;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  border: none;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

.tips {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: left;
}

.tips h3 {
  color: #0369a1;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips li {
  color: #0c4a6e;
  padding: 0.25rem 0;
  position: relative;
  padding-left: 1.5rem;
}

.tips li::before {
  content: '•';
  color: #3b82f6;
  font-weight: bold;
  position: absolute;
  left: 0;
}

@media (max-width: 640px) {
  .success-card {
    padding: 2rem 1rem;
  }
  
  .success-title {
    font-size: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .activation-code {
    word-break: break-all;
  }
}
</style>
