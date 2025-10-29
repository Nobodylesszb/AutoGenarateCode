<template>
  <div class="admin">
    <div class="container">
      <div class="admin-header">
        <h2>管理后台</h2>
        <div class="admin-actions">
          <button @click="refreshData" class="btn btn-secondary">刷新数据</button>
          <button @click="generateCodes" class="btn">生成激活码</button>
        </div>
      </div>
      
      <div class="card mb-2">
        <h3 class="mb-2">使用趋势（最近7天）</h3>
        <svg :width="chartWidth" :height="chartHeight">
          <polyline
            :points="polylinePoints"
            fill="rgba(102,126,234,0.3)"
            stroke="rgba(102,126,234,1)"
            stroke-width="2"
          />
          <g v-for="(p,i) in plottedPoints" :key="i">
            <circle :cx="p.x" :cy="p.y" r="3" fill="#4f46e5" />
          </g>
        </svg>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <h3>总激活码数</h3>
          <div class="stat-number">{{ stats.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <h3>已使用</h3>
          <div class="stat-number">{{ stats.used || 0 }}</div>
        </div>
        <div class="stat-card">
          <h3>未使用</h3>
          <div class="stat-number">{{ stats.unused || 0 }}</div>
        </div>
        <div class="stat-card">
          <h3>已过期</h3>
          <div class="stat-number">{{ stats.expired || 0 }}</div>
        </div>
      </div>
      
      <div class="admin-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="['tab-button', { active: activeTab === tab.key }]"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="tab-content">
        <!-- 激活码管理 -->
        <div v-if="activeTab === 'codes'" class="codes-section">
          <div class="section-header">
            <h3>激活码管理</h3>
            <div class="filters">
              <select v-model="codeFilter" class="form-input">
                <option value="">全部状态</option>
                <option value="unused">未使用</option>
                <option value="used">已使用</option>
                <option value="expired">已过期</option>
                <option value="disabled">已禁用</option>
              </select>
            </div>
          </div>
          
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>激活码</th>
                  <th>产品</th>
                  <th>状态</th>
                  <th>价格</th>
                  <th>创建时间</th>
                  <th>使用时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="code in filteredCodes" :key="code.id">
                  <td class="code-cell">
                    <code>{{ code.code }}</code>
                    <button @click="copyCode(code.code)" class="copy-btn">复制</button>
                  </td>
                  <td>{{ code.product_name }}</td>
                  <td>
                    <span :class="['status-badge', code.status]">
                      {{ getStatusText(code.status) }}
                    </span>
                  </td>
                  <td>¥{{ code.price }}</td>
                  <td>{{ formatDate(code.created_at) }}</td>
                  <td>{{ code.used_at ? formatDate(code.used_at) : '-' }}</td>
                  <td>
                    <button 
                      @click="toggleCodeStatus(code)" 
                      :class="['btn', 'btn-sm', code.status === 'disabled' ? 'btn-success' : 'btn-danger']"
                    >
                      {{ code.status === 'disabled' ? '启用' : '禁用' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- 支付记录 -->
        <div v-if="activeTab === 'payments'" class="payments-section">
          <div class="section-header">
            <h3>支付记录</h3>
          </div>
          
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>支付ID</th>
                  <th>激活码</th>
                  <th>金额</th>
                  <th>支付方式</th>
                  <th>状态</th>
                  <th>支付时间</th>
                  <th>创建时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="payment in payments" :key="payment.id">
                  <td>{{ payment.payment_id }}</td>
                  <td>{{ payment.activation_code?.code || '-' }}</td>
                  <td>¥{{ payment.amount }}</td>
                  <td>{{ payment.method === 'wechat' ? '微信支付' : '支付宝' }}</td>
                  <td>
                    <span :class="['status-badge', payment.status]">
                      {{ getPaymentStatusText(payment.status) }}
                    </span>
                  </td>
                  <td>{{ payment.paid_at ? formatDate(payment.paid_at) : '-' }}</td>
                  <td>{{ formatDate(payment.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- 产品管理 -->
        <div v-if="activeTab === 'products'" class="products-section">
          <div class="section-header">
            <h3>产品管理</h3>
            <button @click="showProductForm = true" class="btn">添加产品</button>
          </div>
          
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>产品ID</th>
                  <th>产品名称</th>
                  <th>描述</th>
                  <th>价格</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in products" :key="product.id">
                  <td>{{ product.product_id }}</td>
                  <td>{{ product.name }}</td>
                  <td>{{ product.description || '-' }}</td>
                  <td>¥{{ product.price }}</td>
                  <td>
                    <span :class="['status-badge', product.is_active ? 'active' : 'inactive']">
                      {{ product.is_active ? '启用' : '禁用' }}
                    </span>
                  </td>
                  <td>{{ formatDate(product.created_at) }}</td>
                  <td>
                    <button @click="editProduct(product)" class="btn btn-sm btn-secondary">编辑</button>
                    <button @click="deleteProduct(product.id)" class="btn btn-sm btn-danger">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- 生成激活码模态框 -->
      <div v-if="showGenerateModal" class="modal-overlay" @click="showGenerateModal = false">
        <div class="modal" @click.stop>
          <h3>生成激活码</h3>
          <form @submit.prevent="handleGenerateCodes">
            <div class="form-group">
              <label class="form-label">产品</label>
              <select v-model="generateForm.product_id" class="form-input" required>
                <option value="">选择产品</option>
                <option v-for="product in products" :key="product.product_id || product.id" :value="product.product_id">
                  {{ product.product_name || product.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">生成数量</label>
              <input 
                type="number" 
                v-model="generateForm.quantity" 
                min="1" 
                max="1000" 
                class="form-input"
                required
              >
            </div>
            <div class="form-group">
              <label class="form-label">过期天数</label>
              <input 
                type="number" 
                v-model="generateForm.expire_days" 
                min="1" 
                max="3650" 
                class="form-input"
                placeholder="365"
              >
            </div>
            <div class="modal-actions">
              <button type="button" @click="showGenerateModal = false" class="btn btn-secondary">取消</button>
              <button type="submit" class="btn" :disabled="isGenerating">
                {{ isGenerating ? '生成中...' : '生成激活码' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/api'

export default {
  name: 'Admin',
  setup() {
    const activeTab = ref('codes')
    const stats = ref({})
    const trendPoints = ref([])
    const codes = ref([])
    const payments = ref([])
    const products = ref([])
    const codeFilter = ref('')
    const showGenerateModal = ref(false)
    const isGenerating = ref(false)
    
    const generateForm = ref({
      product_id: '',
      quantity: 1,
      expire_days: 365
    })
    
    const tabs = [
      { key: 'codes', label: '激活码管理' },
      { key: 'payments', label: '支付记录' },
      { key: 'products', label: '产品管理' }
    ]
    
    // 简易折线图
    const chartWidth = 600
    const chartHeight = 200
    const padding = 30
    const plottedPoints = computed(() => {
      if (!trendPoints.value.length) return []
      const maxY = Math.max(...trendPoints.value.map(d => d.count), 1)
      const stepX = (chartWidth - padding * 2) / (trendPoints.value.length - 1)
      return trendPoints.value.map((d, i) => {
        const x = padding + i * stepX
        const y = padding + (1 - d.count / maxY) * (chartHeight - padding * 2)
        return { x, y }
      })
    })
    const polylinePoints = computed(() => {
      if (!plottedPoints.value.length) return ''
      const left = `${padding},${chartHeight - padding}`
      const line = plottedPoints.value.map(p => `${p.x},${p.y}`).join(' ')
      const right = `${padding + (plottedPoints.value.length - 1) * ((chartWidth - padding * 2) / (plottedPoints.value.length - 1))},${chartHeight - padding}`
      return `${left} ${line} ${right}`
    })
    
    const filteredCodes = computed(() => {
      if (!codeFilter.value) return codes.value
      return codes.value.filter(code => code.status === codeFilter.value)
    })
    
    const getStatusText = (status) => {
      const statusMap = {
        'unused': '未使用',
        'used': '已使用',
        'expired': '已过期',
        'disabled': '已禁用'
      }
      return statusMap[status] || status
    }
    
    const getPaymentStatusText = (status) => {
      const statusMap = {
        'pending': '待支付',
        'paid': '已支付',
        'failed': '支付失败',
        'refunded': '已退款'
      }
      return statusMap[status] || status
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    const copyCode = async (code) => {
      try {
        await navigator.clipboard.writeText(code)
        alert('激活码已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
      }
    }
    
    const refreshData = async () => {
      try {
        // 获取仪表盘统计（受保护）
        const s = await api.admin.getDashboardStats()
        stats.value = {
          total: s.total_codes,
          used: s.used_codes,
          unused: (s.total_codes || 0) - (s.used_codes || 0),
          expired: 0
        }
        trendPoints.value = s.usage_trend || []
        
        // 获取激活码列表
        const codesResponse = await api.admin.getAllCodes()
        codes.value = codesResponse
        
        // 获取支付记录
        const paymentsResponse = await api.admin.getAllPayments()
        payments.value = paymentsResponse
        
        // 获取产品列表
        const productsResponse = await api.products.getProducts()
        products.value = productsResponse
        
      } catch (error) {
        console.error('刷新数据失败:', error)
      }
    }
    
    const generateCodes = () => {
      showGenerateModal.value = true
    }
    
    const handleGenerateCodes = async () => {
      isGenerating.value = true
      
      try {
        const product = products.value.find(p => p.product_id === generateForm.value.product_id)
        if (!product) {
          alert('请选择产品')
          return
        }
        
        const expireDate = new Date()
        expireDate.setDate(expireDate.getDate() + generateForm.value.expire_days)
        
        await api.activation.generateCodes({
          product_id: generateForm.value.product_id,
          product_name: product.product_name || product.name,
          price: product.price,
          quantity: generateForm.value.quantity,
          expires_at: expireDate.toISOString()
        })
        
        alert('激活码生成成功')
        showGenerateModal.value = false
        refreshData()
        
      } catch (error) {
        console.error('生成激活码失败:', error)
        alert('生成激活码失败')
      } finally {
        isGenerating.value = false
      }
    }
    
    const toggleCodeStatus = async (code) => {
      try {
        // 这里应该调用API切换状态
        alert('状态切换功能待实现')
      } catch (error) {
        console.error('切换状态失败:', error)
      }
    }
    
    const editProduct = (product) => {
      alert('编辑产品功能待实现')
    }
    
    const deleteProduct = async (id) => {
      if (confirm('确定要删除这个产品吗？')) {
        try {
          await api.products.deleteProduct(id)
          alert('产品删除成功')
          refreshData()
        } catch (error) {
          console.error('删除产品失败:', error)
          alert('删除产品失败')
        }
      }
    }
    
    onMounted(() => {
      refreshData()
    })
    
    return {
      activeTab,
      tabs,
      stats,
      chartWidth,
      chartHeight,
      plottedPoints,
      polylinePoints,
      trendPoints,
      codes,
      payments,
      products,
      codeFilter,
      filteredCodes,
      showGenerateModal,
      isGenerating,
      generateForm,
      getStatusText,
      getPaymentStatusText,
      formatDate,
      copyCode,
      refreshData,
      generateCodes,
      handleGenerateCodes,
      toggleCodeStatus,
      editProduct,
      deleteProduct
    }
  }
}
</script>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.admin-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
}

.admin-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: white;
  border: 2px solid #e1e5e9;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
}

.table-container {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e1e5e9;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.code-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.code-cell code {
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-family: monospace;
}

.copy-btn {
  padding: 0.25rem 0.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 0.8rem;
  cursor: pointer;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.unused {
  background: #d4edda;
  color: #155724;
}

.status-badge.used {
  background: #cce5ff;
  color: #004085;
}

.status-badge.expired {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.disabled {
  background: #e2e3e5;
  color: #383d41;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.paid {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #e2e3e5;
  color: #383d41;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .admin-actions {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .data-table {
    font-size: 0.9rem;
  }
  
  .data-table th,
  .data-table td {
    padding: 0.5rem;
  }
}
</style>
