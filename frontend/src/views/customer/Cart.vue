<template>
  <div class="cart-page" :class="{ 'from-product-detail': isFromProductDetail }">
    <div class="page-header" v-if="isFromProductDetail">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">购物车</h1>
    </div>
    <div class="page-header no-back" v-else>
      <h1 class="page-title">购物车</h1>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">🛒</div>
      <p>购物车是空的</p>
      <router-link to="/customer/home" class="go-shopping-btn">去购物</router-link>
    </div>
    
    <div v-else>
      <div class="cart-list">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <div class="item-image">
            <img :src="getProductImage(item)" :alt="item.product_name" />
          </div>
          <div class="item-info">
            <div class="item-name">{{ item.product_name }}</div>
            <div class="item-price">¥{{ formatPrice(item.price) }}</div>
            <div class="item-quantity">
              <button class="quantity-btn" @click="decreaseQuantity(item)" :disabled="item.quantity <= 1">-
              </button>
              <span class="quantity">{{ item.quantity }}</span>
              <button class="quantity-btn" @click="increaseQuantity(item)">+</button>
            </div>
          </div>
          <button class="remove-btn" @click="removeItem(item.id)">
            <span>×</span>
          </button>
        </div>
      </div>
      
      <div class="cart-summary">
        <div class="summary-content">
          <div class="cart-info">
            <div class="cart-items">
              <span class="item-count">{{ totalQuantity }}</span>
              <span class="item-label">件商品</span>
            </div>
            <div class="cart-total">
              <span class="total-label">合计：</span>
              <span class="total-price">¥{{ formatPrice(totalPrice) }}</span>
            </div>
          </div>
          <button 
            class="checkout-btn" 
            @click="checkout"
            :disabled="cartItems.length === 0"
          >
            结算
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as cartApi from '../../api/cart'

const router = useRouter()
const route = useRoute()

// 从商品详情页面进入购物车
const isFromProductDetail = computed(() => {
  const from = sessionStorage.getItem('fromRoute')
  return from === '/customer/product-detail'
})

const cartItems = ref([])
const loading = ref(false)

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const totalQuantity = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
})

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const getProductImage = (product) => {
  if (product.product_image) {
    if (product.product_image.startsWith('http')) {
      return product.product_image
    }
    return window.location.origin + product.product_image
  }
  return `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(product.product_name || '商品')}&image_size=square`
}

const fetchCart = async () => {
  loading.value = true
  try {
    const response = await cartApi.getCartItems()
    cartItems.value = response.items || []
  } catch (err) {
    console.error('获取购物车失败:', err)
    ElMessage.error('获取购物车失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const increaseQuantity = async (item) => {
  const oldQuantity = item.quantity
  try {
    item.quantity++
    const response = await cartApi.updateCartItem(item.id, { quantity: item.quantity })
    cartItems.value = response.cart.items
    ElMessage.success('数量已更新')
  } catch (err) {
    console.error('更新数量失败:', err)
    ElMessage.error('更新数量失败，请稍后重试')
    item.quantity = oldQuantity
  }
}

const decreaseQuantity = async (item) => {
  if (item.quantity > 1) {
    const oldQuantity = item.quantity
    try {
      item.quantity--
      const response = await cartApi.updateCartItem(item.id, { quantity: item.quantity })
      cartItems.value = response.cart.items
      ElMessage.success('数量已更新')
    } catch (err) {
      console.error('更新数量失败:', err)
      ElMessage.error('更新数量失败，请稍后重试')
      item.quantity = oldQuantity
    }
  }
}

const removeItem = async (itemId) => {
  const oldCartItems = [...cartItems.value]
  try {
    const response = await cartApi.removeCartItem(itemId)
    cartItems.value = response.cart.items
    ElMessage.success('商品已从购物车中删除')
  } catch (err) {
    console.error('删除商品失败:', err)
    ElMessage.error('删除商品失败，请稍后重试')
    cartItems.value = oldCartItems
  }
}

const checkout = () => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('购物车是空的')
    return
  }
  // 跳转到结算页面，传递购物车数据
  router.push({
    name: 'OrderCheckout',
    state: { cartItems: cartItems.value }
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  // 检查是否从商品详情页面进入
  const isFromProductDetailPage = sessionStorage.getItem('fromRoute') === '/customer/product-detail'
  
  // 如果不是从商品详情页面进入，清除来源记录
  if (!isFromProductDetailPage) {
    sessionStorage.removeItem('fromRoute')
  }
  
  fetchCart()
})
</script>

<style scoped>
.cart-page {
  padding: 16px;
  padding-bottom: 100px;
  min-height: 100vh;
  background-color: #f5f7fa;
  box-sizing: border-box;
}

.cart-page.from-product-detail {
  padding-bottom: 100px;
}

.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  background: white;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  z-index: 100;
  margin: 0;
  gap: 12px;
}

.page-header.no-back {
  position: static;
  box-shadow: none;
  border-bottom: none;
  padding: 0 0 16px 0;
  margin-bottom: 16px;
}

.page-header.no-back .page-title {
  text-align: center;
  width: 100%;
}

.back-btn {
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

.back-btn:hover {
  background: #e5e7eb;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

.cart-list {
  margin-top: 80px;
  margin-bottom: 20px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #9ca3af;
  font-size: 16px;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-cart p {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 24px;
}

.go-shopping-btn {
  display: inline-block;
  padding: 12px 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  text-decoration: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.go-shopping-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.cart-list {
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.cart-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.item-image {
  width: 90px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 16px;
  flex-shrink: 0;
  background: #f9fafb;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.cart-item:hover .item-image img {
  transform: scale(1.05);
}

.item-info {
  flex: 1;
  margin-right: 16px;
  min-width: 0;
}

.item-name {
  font-size: 15px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.item-price {
  font-size: 18px;
  font-weight: 600;
  color: #ef4444;
  margin-bottom: 12px;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.quantity-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.quantity-btn:disabled {
  border-color: #e5e7eb;
  color: #d1d5db;
  cursor: not-allowed;
}

.quantity {
  font-size: 16px;
  font-weight: 500;
  min-width: 32px;
  text-align: center;
  color: #1f2937;
}

.remove-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 24px;
  font-weight: 300;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #ef4444;
  color: white;
  transform: scale(1.1);
}

.cart-summary {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  z-index: 999;
  padding: 12px 16px;
}

.cart-page:not(.from-product-detail) .cart-summary {
  bottom: 60px; /* 导航栏高度 */
}

.summary-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 480px;
  margin: 0 auto;
}

.cart-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.cart-items {
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-count {
  font-size: 16px;
  font-weight: 600;
  color: #3b82f6;
}

.item-label {
  font-size: 14px;
  color: #6b7280;
}

.cart-total {
  display: flex;
  align-items: center;
  gap: 4px;
}

.total-label {
  font-size: 14px;
  color: #6b7280;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
  color: #ef4444;
}

.checkout-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.checkout-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.checkout-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@media (min-width: 768px) {
  .cart-page {
    max-width: 480px;
    margin: 0 auto;
  }
  
  .cart-summary {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 12px 12px 0 0;
  }
}
</style>
