<template>
  <div class="payment-admin">
    <div class="container">
      <div class="header">
        <h1>支付管理</h1>
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-value">¥{{ statistics.total_amount || 0 }}</div>
            <div class="stat-label">总支付金额</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.total_orders || 0 }}</div>
            <div class="stat-label">总订单数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">¥{{ statistics.today_amount || 0 }}</div>
            <div class="stat-label">今日金额</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.today_orders || 0 }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </div>
      </div>
      
      <div class="filters">
        <div class="filter-group">
          <label>支付状态：</label>
          <select v-model="filters.status" @change="fetchPayments">
            <option value="">全部</option>
            <option value="pending">待支付</option>
            <option value="paid">已支付</option>
            <option value="failed">支付失败</option>
            <option value="refunded">已退款</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>支付方式：</label>
          <select v-model="filters.method" @change="fetchPayments">
            <option value="">全部</option>
            <option value="wechat">微信支付</option>
            <option value="alipay">支付宝</option>
          </select>
        </div>
        
        <button @click="refreshData" class="btn btn-primary">
          <i class="fas fa-sync-alt"></i>
          刷新
        </button>
      </div>
      
      <div class="table-container">
        <table class="payments-table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>激活码ID</th>
              <th>金额</th>
              <th>支付方式</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>支付时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in payments" :key="payment.id">
              <td>{{ payment.payment_id }}</td>
              <td>{{ payment.activation_code_id }}</td>
              <td>¥{{ payment.amount }}</td>
              <td>
                <span class="method-badge" :class="payment.method">
                  {{ payment.method === 'wechat' ? '微信' : '支付宝' }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="payment.status">
                  {{ getStatusText(payment.status) }}
                </span>
              </td>
              <td>{{ formatDate(payment.created_at) }}</td>
              <td>{{ payment.paid_at ? formatDate(payment.paid_at) : '-' }}</td>
              <td>
                <div class="actions">
                  <button 
                    v-if="payment.status === 'paid'" 
                    @click="handleRefund(payment)"
                    class="btn btn-sm btn-warning"
                  >
                    退款
                  </button>
                  <button 
                    @click="viewDetails(payment)"
                    class="btn btn-sm btn-secondary"
                  >
                    详情
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="loading">
          <i class="fas fa-spinner fa-spin"></i>
          加载中...
        </div>
        
        <div v-if="!loading && payments.length === 0" class="empty">
          暂无支付记录
        </div>
      </div>
      
      <div class="pagination">
        <button 
          @click="prevPage" 
          :disabled="currentPage === 1"
          class="btn btn-secondary"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        <button 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          class="btn btn-secondary"
        >
          下一页
        </button>
      </div>
    </div>
    
    <!-- 退款确认对话框 -->
    <div v-if="showRefundDialog" class="modal-overlay" @click="closeRefundDialog">
      <div class="modal" @click.stop>
        <h3>确认退款</h3>
        <div class="refund-info">
          <p><strong>订单号：</strong>{{ selectedPayment?.payment_id }}</p>
          <p><strong>金额：</strong>¥{{ selectedPayment?.amount }}</p>
        </div>
        <div class="form-group">
          <label>退款原因：</label>
          <textarea 
            v-model="refundReason" 
            placeholder="请输入退款原因"
            rows="3"
          ></textarea>
        </div>
        <div class="modal-actions">
          <button @click="closeRefundDialog" class="btn btn-secondary">取消</button>
          <button @click="confirmRefund" class="btn btn-danger">确认退款</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/api/api'

const payments = ref([])
const statistics = ref({})
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = ref(1)

const filters = ref({
  status: '',
  method: ''
})

const showRefundDialog = ref(false)
const selectedPayment = ref(null)
const refundReason = ref('用户申请退款')

const fetchPayments = async () => {
  loading.value = true
  
  try {
    const response = await api.payment.getPaymentList(
      (currentPage.value - 1) * pageSize.value,
      pageSize.value,
      filters.value.status || null
    )
    
    payments.value = response
    
  } catch (error) {
    console.error('获取支付列表失败:', error)
    alert('获取支付列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const response = await api.payment.getPaymentStatistics()
    statistics.value = response
  } catch (error) {
    console.error('获取支付统计失败:', error)
  }
}

const refreshData = () => {
  fetchPayments()
  fetchStatistics()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchPayments()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchPayments()
  }
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待支付',
    paid: '已支付',
    failed: '支付失败',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const handleRefund = (payment) => {
  selectedPayment.value = payment
  refundReason.value = '用户申请退款'
  showRefundDialog.value = true
}

const closeRefundDialog = () => {
  showRefundDialog.value = false
  selectedPayment.value = null
}

const confirmRefund = async () => {
  if (!selectedPayment.value) return
  
  try {
    const response = await api.payment.refundPayment(
      selectedPayment.value.payment_id,
      refundReason.value
    )
    
    if (response.success) {
      alert('退款处理成功')
      closeRefundDialog()
      refreshData()
    } else {
      alert('退款处理失败')
    }
    
  } catch (error) {
    console.error('退款处理失败:', error)
    alert('退款处理失败')
  }
}

const viewDetails = (payment) => {
  // 可以跳转到支付详情页面
  console.log('查看支付详情:', payment)
}

onMounted(() => {
  fetchPayments()
  fetchStatistics()
})
</script>

<style scoped>
.payment-admin {
  padding: 2rem;
  background: #f8fafc;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #374151;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.payments-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.payments-table tr:hover {
  background: #f9fafb;
}

.method-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.method-badge.wechat {
  background: #dcfce7;
  color: #166534;
}

.method-badge.alipay {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.paid {
  background: #dcfce7;
  color: #166534;
}

.status-badge.failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.refunded {
  background: #e0e7ff;
  color: #3730a3;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  color: #6b7280;
  font-weight: 600;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 1rem;
  color: #1f2937;
}

.refund-info {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.refund-info p {
  margin: 0.5rem 0;
  color: #374151;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .payment-admin {
    padding: 1rem;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .payments-table {
    font-size: 0.875rem;
  }
  
  .payments-table th,
  .payments-table td {
    padding: 0.5rem;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>
