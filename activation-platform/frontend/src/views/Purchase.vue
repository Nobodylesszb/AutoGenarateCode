<template>
  <div class="purchase">
    <div class="container">
      <div class="card">
        <h2>购买激活码</h2>
        
        <form @submit.prevent="handlePurchase" class="purchase-form">
          <div class="form-group">
            <label class="form-label">选择产品</label>
            <select v-model="selectedProduct" class="form-input" required>
              <option value="">请选择产品</option>
              <option v-for="product in products" :key="product.id" :value="product">
                {{ product.name }} - ¥{{ product.price }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">支付方式</label>
            <div class="payment-methods">
              <label class="payment-method">
                <input type="radio" v-model="paymentMethod" value="wechat" required>
                <span class="payment-icon">💚</span>
                <span>微信支付</span>
              </label>
              <label class="payment-method">
                <input type="radio" v-model="paymentMethod" value="alipay" required>
                <span class="payment-icon">🔵</span>
                <span>支付宝</span>
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">购买数量</label>
            <input 
              type="number" 
              v-model="quantity" 
              min="1" 
              max="10" 
              class="form-input"
              required
            >
          </div>
          
          <div class="order-summary">
            <h3>订单摘要</h3>
            <div class="summary-item">
              <span>产品:</span>
              <span>{{ selectedProduct?.name || '未选择' }}</span>
            </div>
            <div class="summary-item">
              <span>单价:</span>
              <span>¥{{ selectedProduct?.price || 0 }}</span>
            </div>
            <div class="summary-item">
              <span>数量:</span>
              <span>{{ quantity }}</span>
            </div>
            <div class="summary-item total">
              <span>总计:</span>
              <span>¥{{ totalPrice }}</span>
            </div>
          </div>
          
          <button type="submit" class="btn" :disabled="!canPurchase">
            {{ isProcessing ? '处理中...' : '立即购买' }}
          </button>
        </form>
        
        <div v-if="paymentInfo" class="payment-info">
          <h3>支付信息</h3>
          <div class="alert alert-info">
            <p>订单号: {{ paymentInfo.payment_id }}</p>
            <p>支付金额: ¥{{ paymentInfo.amount }}</p>
            <p>支付方式: {{ paymentMethod === 'wechat' ? '微信支付' : '支付宝' }}</p>
          </div>
          
          <div v-if="paymentInfo.payment_url" class="payment-actions">
            <a :href="paymentInfo.payment_url" target="_blank" class="btn btn-success">
              前往支付
            </a>
          </div>
          
          <div v-if="paymentInfo.qr_code" class="qr-code">
            <h4>扫码支付</h4>
            <div class="qr-placeholder">
              <p>二维码: {{ paymentInfo.qr_code }}</p>
            </div>
          </div>
        </div>
        
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/api'

export default {
  name: 'Purchase',
  setup() {
    const products = ref([])
    const selectedProduct = ref(null)
    const paymentMethod = ref('')
    const quantity = ref(1)
    const paymentInfo = ref(null)
    const error = ref('')
    const isProcessing = ref(false)
    
    const totalPrice = computed(() => {
      if (!selectedProduct.value) return 0
      return (selectedProduct.value.price * quantity.value).toFixed(2)
    })
    
    const canPurchase = computed(() => {
      return selectedProduct.value && paymentMethod.value && quantity.value > 0
    })
    
    const fetchProducts = async () => {
      try {
        // 模拟数据
        products.value = [
          {
            id: 1,
            product_id: 'premium_license',
            name: '高级版许可证',
            description: '包含所有高级功能的高级版许可证',
            price: 99.00
          },
          {
            id: 2,
            product_id: 'basic_license',
            name: '基础版许可证',
            description: '包含基础功能的基础版许可证',
            price: 29.00
          }
        ]
      } catch (error) {
        console.error('获取产品列表失败:', error)
      }
    }
    
    const handlePurchase = async () => {
      if (!canPurchase.value) return
      
      isProcessing.value = true
      error.value = ''
      
      try {
        // 调用API创建支付订单并生成激活码
        const response = await api.payment.createPaymentWithProduct({
          product_id: selectedProduct.value.product_id,
          product_name: selectedProduct.value.name,
          price: parseFloat(totalPrice.value),
          method: paymentMethod.value,
          max_activations: 1, // 可以根据产品类型设置
          return_url: window.location.origin + '/purchase/success'
        })
        
        if (response.success) {
          paymentInfo.value = {
            payment_id: response.payment_id,
            activation_code_id: response.activation_code_id,
            activation_code: response.activation_code,
            amount: response.amount,
            payment_url: response.payment_url,
            qr_code: response.qr_code,
            product_name: response.product_name
          }
          
          // 如果支付成功，跳转到成功页面
          if (response.payment_url) {
            // 可以在这里添加支付状态轮询
            startPaymentStatusPolling(response.payment_id)
          }
        } else {
          error.value = '创建支付订单失败，请重试'
        }
        
      } catch (err) {
        error.value = '创建支付订单失败，请重试'
        console.error('Purchase error:', err)
      } finally {
        isProcessing.value = false
      }
    }
    
    const startPaymentStatusPolling = (paymentId) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await api.payment.getPaymentStatus(paymentId)
          if (status.status === 'paid') {
            clearInterval(pollInterval)
            // 支付成功，可以跳转到成功页面或显示成功信息
            await handlePaymentSuccess(paymentId)
          }
        } catch (err) {
          console.error('Payment status polling error:', err)
        }
      }, 3000) // 每3秒检查一次
      
      // 5分钟后停止轮询
      setTimeout(() => {
        clearInterval(pollInterval)
      }, 300000)
    }
    
    const handlePaymentSuccess = async (paymentId) => {
      try {
        const successInfo = await api.payment.getPaymentSuccessInfo(paymentId)
        if (successInfo.success) {
          // 显示支付成功信息
          alert(`支付成功！您的激活码是：${successInfo.activation_code}`)
          // 可以跳转到激活页面
          // router.push(`/activation?code=${successInfo.activation_code}`)
        }
      } catch (err) {
        console.error('Get payment success info error:', err)
      }
    }
    
    onMounted(() => {
      fetchProducts()
    })
    
    return {
      products,
      selectedProduct,
      paymentMethod,
      quantity,
      paymentInfo,
      error,
      isProcessing,
      totalPrice,
      canPurchase,
      handlePurchase
    }
  }
}
</script>

<style scoped>
.purchase-form {
  max-width: 600px;
  margin: 0 auto;
}

.payment-methods {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 5px;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.payment-method:hover {
  border-color: #667eea;
}

.payment-method input[type="radio"] {
  margin: 0;
}

.payment-method input[type="radio"]:checked + .payment-icon + span {
  color: #667eea;
  font-weight: 600;
}

.payment-icon {
  font-size: 1.5rem;
}

.order-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 5px;
  margin: 2rem 0;
}

.order-summary h3 {
  margin-bottom: 1rem;
  color: #333;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.summary-item.total {
  font-weight: 700;
  font-size: 1.1rem;
  color: #667eea;
  border-top: 1px solid #dee2e6;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
}

.payment-info {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #dee2e6;
}

.payment-info h3 {
  margin-bottom: 1rem;
  color: #333;
}

.payment-actions {
  margin: 1rem 0;
}

.qr-code {
  margin-top: 1rem;
}

.qr-code h4 {
  margin-bottom: 0.5rem;
  color: #333;
}

.qr-placeholder {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  text-align: center;
  border: 2px dashed #dee2e6;
}

@media (max-width: 768px) {
  .payment-methods {
    flex-direction: column;
  }
  
  .payment-method {
    justify-content: center;
  }
}
</style>
