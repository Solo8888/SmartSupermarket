<template>
  <div class="cart-page">
    <h1 class="page-title">购物车</h1>
    
    <div v-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">🛒</div>
      <p>购物车是空的</p>
      <router-link to="/customer" class="go-shopping-btn">去购物</router-link>
    </div>
    
    <div v-else>
      <div class="cart-list">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <div class="item-image">
            <img :src="getProductImage(item)" :alt="item.name" />
          </div>
          <div class="item-info">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-price">¥{{ formatPrice(item.price) }}</div>
            <div class="item-quantity">
              <button class="quantity-btn" @click="decreaseQuantity(item)">-</button>
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
        <div class="total-price">
          <span>合计：</span>
          <span class="price">¥{{ formatPrice(totalPrice) }}</span>
        </div>
        <button class="checkout-btn" @click="checkout">结算 ({{ totalQuantity }})</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const cartItems = ref([])

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
  if (product.imageUrl) {
    return product.imageUrl
  }
  return `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(product.name || '商品')}&image_size=square`
}

const increaseQuantity = (item) => {
  item.quantity++
}

const decreaseQuantity = (item) => {
  if (item.quantity > 1) {
    item.quantity--
  }
}

const removeItem = (itemId) => {
  cartItems.value = cartItems.value.filter(item => item.id !== itemId)
}

const checkout = () => {
  alert('结算功能开发中...')
}
</script>

<style scoped>
.cart-page {
  padding: 16px;
  padding-bottom: 80px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-cart p {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.go-shopping-btn {
  display: inline-block;
  padding: 12px 32px;
  background-color: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 24px;
  font-size: 16px;
}

.cart-list {
  margin-bottom: 16px;
}

.cart-item {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  margin-right: 12px;
}

.item-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-price {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
  margin-bottom: 8px;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity {
  font-size: 15px;
  min-width: 24px;
  text-align: center;
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background-color: #f5f5f5;
  color: #999;
  font-size: 24px;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-summary {
  position: fixed;
  bottom: 70px;
  left: 0;
  right: 0;
  background-color: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.total-price {
  font-size: 15px;
  color: #333;
}

.total-price .price {
  font-size: 20px;
  font-weight: 600;
  color: #ff4d4f;
}

.checkout-btn {
  padding: 12px 32px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}
</style>
