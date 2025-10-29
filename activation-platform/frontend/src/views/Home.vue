<template>
  <div class="home">
    <div class="container">
      <div class="hero">
        <h1>激活码平台</h1>
        <p>安全、便捷的激活码生成和管理平台</p>
        <div class="hero-actions">
          <router-link to="/purchase" class="btn">购买激活码</router-link>
          <router-link to="/activation" class="btn btn-secondary">验证激活码</router-link>
        </div>
      </div>
      
      <div class="features">
        <h2>平台特色</h2>
        <div class="grid grid-3">
          <div class="feature-card">
            <div class="feature-icon">🔐</div>
            <h3>安全可靠</h3>
            <p>采用先进的加密算法，确保激活码的安全性和唯一性</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💳</div>
            <h3>多种支付</h3>
            <p>支持微信支付、支付宝等多种支付方式，支付便捷</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>数据统计</h3>
            <p>提供详细的激活码使用统计和管理功能</p>
          </div>
        </div>
      </div>
      
      <div class="products">
        <h2>热门产品</h2>
        <div class="grid grid-2">
          <div class="product-card" v-for="product in products" :key="product.id">
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            <div class="product-price">
              <span class="price">¥{{ product.price }}</span>
              <router-link :to="`/purchase?product=${product.product_id}`" class="btn">立即购买</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from '../api/api'

export default {
  name: 'Home',
  setup() {
    const products = ref([])
    
    const fetchProducts = async () => {
      try {
        // 这里应该调用API获取产品列表
        // const response = await api.getProducts()
        // products.value = response.data
        
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
    
    onMounted(() => {
      fetchProducts()
    })
    
    return {
      products
    }
  }
}
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.features {
  margin-bottom: 3rem;
}

.features h2 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  color: #333;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.products {
  margin-bottom: 3rem;
}

.products h2 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  color: #333;
}

.product-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.product-card h3 {
  margin-bottom: 1rem;
  color: #333;
}

.product-card p {
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.product-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero p {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .product-price {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
