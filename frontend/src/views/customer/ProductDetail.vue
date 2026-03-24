<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as productApi from '../../api/product'
import * as cartApi from '../../api/cart'
import * as reviewApi from '../../api/review'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const loading = ref(true)
const quantity = ref(1)
const reviews = ref([])
const reviewsLoading = ref(false)
const cartItems = ref([])
const cartLoading = ref(false)

const fetchProductDetail = async () => {
  const productId = route.params.id
  loading.value = true
  try {
    product.value = await productApi.getProduct(productId)
    // 获取商品评价
    if (product.value) {
      await fetchReviews(productId)
    }
  } catch (err) {
    console.error('获取商品详情失败:', err)
    ElMessage.error('获取商品详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const addToCart = async () => {
  if (!product.value) return
  
  try {
    await cartApi.addToCart({
      product_id: product.value.id,
      quantity: quantity.value
    })
    ElMessage.success('已添加到购物车')
    // 重新获取购物车数据
    await fetchCart()
  } catch (err) {
    console.error('添加到购物车失败:', err)
    ElMessage.error('添加到购物车失败，请稍后重试')
  }
}

const goBack = () => {
  router.back()
}

const goToCart = () => {
  // 记录来源路由
  sessionStorage.setItem('fromRoute', '/customer/product-detail')
  router.push('/customer/cart')
}

const goToCheckout = () => {
  // 记录来源路由
  sessionStorage.setItem('fromRoute', '/customer/product-detail')
  router.push('/customer/checkout')
}

const fetchCart = async () => {
  cartLoading.value = true
  try {
    const response = await cartApi.getCartItems()
    cartItems.value = response?.items || []
  } catch (err) {
    console.error('获取购物车失败:', err)
  } finally {
    cartLoading.value = false
  }
}

const fetchReviews = async (productId) => {
  reviewsLoading.value = true
  try {
    const response = await reviewApi.getReviewsByProduct(productId)
    reviews.value = response?.items || []
  } catch (err) {
    console.error('获取商品评价失败:', err)
  } finally {
    reviewsLoading.value = false
  }
}

const getProductImage = (product) => {
  if (product.image_url) {
    if (product.image_url.startsWith('http')) {
      return product.image_url
    }
    return window.location.origin + product.image_url
  }
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' + encodeURIComponent(product.name || '商品') + '&image_size=square'
}

onMounted(async () => {
  await fetchProductDetail()
  await fetchCart()
})
</script>

<template>
  <div class="product-detail">
    <div class="page-header">
      <button class="back-button" @click="goBack">
        ←
      </button>
      <h2>商品详情</h2>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!product" class="error">商品不存在</div>
    <div v-else class="product-content">
      <!-- 商品图片 -->
      <div class="product-image">
        <img :src="getProductImage(product)" :alt="product.name" />
      </div>
      
      <!-- 商品信息 -->
      <div class="product-info">
        <h1 class="product-name">{{ product.name }}</h1>
        <div class="product-price">¥{{ parseFloat(product.price).toFixed(2) }}</div>
        
        <!-- 库存信息 -->
        <div class="product-stock" :class="{ 'out-of-stock': product.stock <= 0 }">
          <span class="stock-label">库存：</span>
          <span class="stock-value">{{ product.stock > 0 ? product.stock : '缺货' }}</span>
        </div>
        
        <!-- 商品详情 -->
        <div class="product-details">
          <div class="detail-item">
            <span class="detail-label">品牌：</span>
            <span class="detail-value">{{ product.brand || '无' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">产地：</span>
            <span class="detail-value">{{ product.origin || '无' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">单位：</span>
            <span class="detail-value">{{ product.unit }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">保质期：</span>
            <span class="detail-value">{{ product.shelf_life ? product.shelf_life + '天' : '无' }}</span>
          </div>
        </div>
        
        <!-- 商品描述 -->
        <div class="product-description">
          <h3>商品描述</h3>
          <p>{{ product.description || '暂无描述' }}</p>
        </div>
        
        <!-- 购买区域 -->
        <div class="purchase-area">
          <div class="quantity-control">
            <button class="quantity-btn" @click="quantity = Math.max(1, quantity - 1)">-</button>
            <input type="number" v-model.number="quantity" min="1" class="quantity-input" />
            <button class="quantity-btn" @click="quantity++">+</button>
          </div>
          <button class="add-to-cart-btn" @click="addToCart" :disabled="product.stock <= 0">
            {{ product.stock > 0 ? '添加到购物车' : '缺货' }}
          </button>
        </div>
        
        <!-- 商品评价 -->
        <div class="product-reviews">
          <h3>商品评价</h3>
          <div v-if="reviewsLoading" class="loading">加载评价中...</div>
          <div v-else-if="reviews.length === 0" class="no-reviews">暂无评价</div>
          <div v-else class="reviews-list">
            <div v-for="review in reviews" :key="review.id" class="review-item">
              <div class="review-header">
                <span class="review-user">{{ review.user_name || '匿名用户' }}</span>
                <span class="review-rating">
                  <span v-for="i in 5" :key="i" class="star" :class="{ 'active': i <= review.rating }">★</span>
                </span>
                <span class="review-date">{{ review.created_at ? new Date(review.created_at).toLocaleString() : '' }}</span>
              </div>
              <div class="review-content">{{ review.content || '用户未留下评价' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部固定按钮 -->
    <div class="bottom-fixed">
      <div class="bottom-left">
        <button class="cart-btn" @click="goToCart">
          <span class="cart-icon">🛒</span>
          <span v-if="cartItems.length > 0" class="cart-count">{{ cartItems.length }}</span>
        </button>
      </div>
      <div class="bottom-middle">
        <div v-if="cartItems.length === 0" class="no-items">未选购商品</div>
        <div v-else class="checkout-info" @click="goToCheckout">
          <span class="checkout-text">去支付</span>
          <span class="checkout-price">¥{{ cartItems.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2) }}</span>
        </div>
      </div>
      <div class="bottom-right">
        <button class="add-to-cart-btn-fixed" @click="addToCart" :disabled="!product || product.stock <= 0">
          {{ product && product.stock > 0 ? '加入购物车' : '缺货' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-detail {
  padding: 16px;
  min-height: 100vh;
  background: #f9fafb;
}

.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  z-index: 100;
  margin: 0;
  border-radius: 0;
}

.back-button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f3f4f6;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.back-button:hover {
  background: #e5e7eb;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.loading, .error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  font-size: 16px;
  color: #6b7280;
}

.product-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 80px;
}

.product-image {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.product-info {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.product-name {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.product-price {
  font-size: 24px;
  font-weight: 700;
  color: #dc2626;
  margin: 0 0 16px 0;
}

.product-stock {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding: 12px;
  background: #f3f4f6;
  border-radius: 8px;
}

.product-stock.out-of-stock {
  background: #fee2e2;
}

.stock-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stock-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.product-stock.out-of-stock .stock-value {
  color: #dc2626;
}

.product-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.product-description {
  margin-bottom: 24px;
}

.product-description h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.product-description p {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
}

.purchase-area {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 4px;
}

.quantity-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.quantity-btn:hover {
  background: #e5e7eb;
}

.quantity-input {
  width: 60px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: white;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.quantity-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.add-to-cart-btn {
  flex: 1;
  min-width: 200px;
  padding: 14px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.add-to-cart-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.add-to-cart-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
}

/* 商品评价样式 */
.product-reviews {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.product-reviews h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.no-reviews {
  text-align: center;
  padding: 32px;
  color: #9ca3af;
  font-size: 14px;
  background: #f9fafb;
  border-radius: 8px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: all 0.2s;
}

.review-item:hover {
  background: #f3f4f6;
  transform: translateY(-2px);
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.review-user {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.review-rating {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 14px;
  color: #d1d5db;
}

.star.active {
  color: #f59e0b;
}

.review-date {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.review-content {
  font-size: 14px;
  line-height: 1.5;
  color: #4b5563;
  margin: 0;
}

@media (min-width: 768px) {
  .product-content {
    flex-direction: row;
  }
  
  .product-image {
    flex: 1;
    max-width: 400px;
  }
  
  .product-info {
    flex: 1;
  }
}

/* 底部固定按钮样式 */
.bottom-fixed {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  background: white;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 99;
  height: 60px;
}

.bottom-left {
  flex: 0 0 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #f3f4f6;
}

.cart-btn {
  position: relative;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc2626;
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.bottom-middle {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-right: 1px solid #f3f4f6;
}

.no-items {
  font-size: 14px;
  color: #6b7280;
}

.checkout-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s;
}

.checkout-info:hover {
  background: #f3f4f6;
}

.checkout-text {
  font-size: 14px;
  color: #374151;
}

.checkout-price {
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
}

.bottom-right {
  flex: 0 0 140px;
  padding: 8px;
}

.add-to-cart-btn-fixed {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.add-to-cart-btn-fixed:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.add-to-cart-btn-fixed:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  box-shadow: none;
}

/* 为内容区域添加底部padding，避免被固定按钮遮挡 */
.product-content {
  padding-bottom: 80px;
}

@media (min-width: 768px) {
  .product-content {
    flex-direction: row;
  }
  
  .product-image {
    flex: 1;
    max-width: 400px;
  }
  
  .product-info {
    flex: 1;
  }
  
  .bottom-fixed {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
  }
}

@media (max-width: 480px) {
  .product-detail {
    padding: 12px;
  }
  
  .product-image {
    padding: 16px;
  }
  
  .product-info {
    padding: 16px;
  }
  
  .product-name {
    font-size: 18px;
  }
  
  .product-price {
    font-size: 20px;
  }
  
  .purchase-area {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quantity-control {
    justify-content: center;
  }
  
  .bottom-right {
    flex: 0 0 120px;
  }
  
  .add-to-cart-btn-fixed {
    font-size: 13px;
  }
  
  .checkout-price {
    font-size: 14px;
  }
}
</style>