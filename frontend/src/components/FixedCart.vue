<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as cartApi from '../api/cart'

const router = useRouter()
const cartItems = ref([])
const loading = ref(false)

// 定义props，接收父组件传递的更新信号
const props = defineProps({
  updateCart: {
    type: Boolean,
    default: false
  }
})

const fetchCart = async () => {
  loading.value = true
  try {
    const response = await cartApi.getCartItems()
    cartItems.value = response.items || []
  } catch (err) {
    console.error('获取购物车失败:', err)
  } finally {
    loading.value = false
  }
}

const totalPrice = computed(() => {
  return cartItems.value.reduce((total, item) => {
    return total + (item.price * item.quantity)
  }, 0)
})

const totalItems = computed(() => {
  return cartItems.value.reduce((total, item) => {
    return total + item.quantity
  }, 0)
})

const navigateToCart = () => {
  router.push('/customer/cart')
}

// 监听更新信号，当接收到更新信号时重新获取购物车数据
watch(() => props.updateCart, (newValue) => {
  if (newValue) {
    fetchCart()
  }
})

onMounted(() => {
  fetchCart()
})
</script>

<template>
  <div class="fixed-cart">
    <div class="cart-content">
      <div class="cart-info">
        <div class="cart-items">
          <span class="item-count">{{ totalItems }}</span>
          <span class="item-label">件商品</span>
        </div>
        <div class="cart-total">
          <span class="total-label">合计：</span>
          <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
        </div>
      </div>
      <button class="checkout-btn" @click="navigateToCart">
        去结算
      </button>
    </div>
  </div>
</template>

<style scoped>
.fixed-cart {
  position: fixed;
  bottom: 60px; /* 导航栏高度 */
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  z-index: 999;
  padding: 12px 16px;
}

.cart-content {
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

.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.checkout-btn:active {
  transform: translateY(0);
}

@media (min-width: 768px) {
  .fixed-cart {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 12px 12px 0 0;
  }
}
</style>
