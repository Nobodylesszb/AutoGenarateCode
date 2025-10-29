// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// HTTP 客户端
class HttpClient {
  constructor(baseURL) {
    this.baseURL = baseURL
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }
    
    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }
  
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' })
  }
  
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
  
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }
  
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' })
  }
}

// 创建 HTTP 客户端实例
const httpClient = new HttpClient(API_BASE_URL)

// API 服务
export const api = {
  // 激活码相关
  activation: {
    // 生成激活码
    generateCodes: (data) => httpClient.post('/api/v1/activation/generate', data),
    
    // 验证激活码
    verifyCode: (code, userId = null) => 
      httpClient.get(`/api/v1/activation/verify/${code}?user_id=${userId || ''}`),
    
    // 使用激活码
    useCode: (code, userId = null) => 
      httpClient.post(`/api/v1/activation/use/${code}`, { user_id: userId }),
    
    // 获取产品激活码列表
    getCodesByProduct: (productId, skip = 0, limit = 100) =>
      httpClient.get(`/api/v1/activation/product/${productId}?skip=${skip}&limit=${limit}`),
    
    // 获取激活码统计
    getStats: (productId = null) => {
      const endpoint = productId 
        ? `/api/v1/activation/stats/${productId}`
        : '/api/v1/activation/stats'
      return httpClient.get(endpoint)
    }
  },
  
  // 支付相关
  payment: {
    // 创建支付订单
    createPayment: (data) => httpClient.post('/api/v1/payment/create', data),
    
    // 创建支付并生成激活码
    createPaymentWithProduct: (data) => 
      httpClient.post('/api/v1/payment/create-with-product', data),
    
    // 获取支付状态
    getPaymentStatus: (paymentId) => 
      httpClient.get(`/api/v1/payment/status/${paymentId}`),
    
    // 获取支付成功信息
    getPaymentSuccessInfo: (paymentId) =>
      httpClient.get(`/api/v1/payment/success/${paymentId}`),
    
    // 退款处理
    refundPayment: (paymentId, reason) =>
      httpClient.post('/api/v1/payment/refund', { payment_id: paymentId, reason }),
    
    // 获取支付统计
    getPaymentStatistics: () =>
      httpClient.get('/api/v1/payment/statistics'),
    
    // 获取支付列表
    getPaymentList: (skip = 0, limit = 100, status = null) => {
      const params = new URLSearchParams({ skip, limit })
      if (status) params.append('status', status)
      return httpClient.get(`/api/v1/payment/list?${params}`)
    }
  },
  
  // 产品相关
  products: {
    // 获取产品列表
    getProducts: () => httpClient.get('/api/v1/products'),
    
    // 创建产品
    createProduct: (data) => httpClient.post('/api/v1/products', data),
    
    // 更新产品
    updateProduct: (id, data) => httpClient.put(`/api/v1/products/${id}`, data),
    
    // 删除产品
    deleteProduct: (id) => httpClient.delete(`/api/v1/products/${id}`)
  },
  
  // 用户认证
  auth: {
    // 登录
    login: (username, password) => 
      httpClient.post('/api/v1/auth/login', { username, password }),
    
    // 注册
    register: (data) => httpClient.post('/api/v1/auth/register', data),
    
    // 获取当前用户信息
    getCurrentUser: () => httpClient.get('/api/v1/auth/me')
  },
  
  // 管理后台
  admin: {
    // 获取所有激活码
    getAllCodes: (skip = 0, limit = 100) =>
      httpClient.get(`/api/v1/admin/activation-codes?skip=${skip}&limit=${limit}`),
    
    // 获取所有支付记录
    getAllPayments: (skip = 0, limit = 100) =>
      httpClient.get(`/api/v1/admin/payments?skip=${skip}&limit=${limit}`),
    
    // 获取系统统计
    getSystemStats: () => httpClient.get('/api/v1/admin/stats')
  }
}

// 导出 HTTP 客户端
export { httpClient }

// 导出 API 基础 URL
export { API_BASE_URL }
