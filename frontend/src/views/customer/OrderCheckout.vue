<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as orderApi from '../../api/order'
import * as addressApi from '../../api/address'
import * as cartApi from '../../api/cart'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const submitting = ref(false)
const addresses = ref([])
const selectedAddressId = ref(null)
const remark = ref('')
const selectedPaymentMethod = ref('')

const cartItems = ref([])

const paymentMethods = [
  { value: 'wechat', label: '微信支付' },
  { value: 'alipay', label: '支付宝支付' }
]

const initCartItems = async () => {
  // 检查是否是支付模式（从订单页面跳转过来）
  if (route.query?.payMode === 'true' && route.query?.orderId) {
    try {
      const orderDetail = await orderApi.getOrder(route.query.orderId)
      cartItems.value = orderDetail.items || []
    } catch (err) {
      console.error('获取订单详情失败:', err)
      ElMessage.error('获取订单详情失败，请重试')
      router.push({ name: 'Orders' })
    }
  } else if (route.state?.cartItems && route.state.cartItems.length > 0) {
    cartItems.value = route.state.cartItems
  } else {
    try {
      const response = await cartApi.getCartItems()
      cartItems.value = response.items || []
    } catch (err) {
      console.error('获取购物车失败:', err)
      cartItems.value = []
    }
  }
}

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const totalQuantity = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
})

const selectedAddress = computed(() => {
  return addresses.value.find(addr => addr.id === selectedAddressId.value)
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

const fetchAddresses = async () => {
  loading.value = true
  try {
    const response = await addressApi.getAddresses()
    addresses.value = response || []
    if (addresses.value.length > 0) {
      const defaultAddress = addresses.value.find(addr => addr.is_default)
      selectedAddressId.value = defaultAddress ? defaultAddress.id : addresses.value[0].id
    }
  } catch (err) {
    console.error('获取地址列表失败:', err)
    ElMessage.error('获取地址列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSubmitOrder = async () => {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  if (cartItems.value.length === 0) {
    ElMessage.warning('购物车是空的')
    return
  }
  if (route.query?.payMode === 'true' && !selectedPaymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  submitting.value = true
  try {
    // 如果是从订单页面跳转过来的支付模式
    if (route.query?.payMode === 'true' && route.query?.orderId) {
      // 直接支付订单
      await orderApi.payOrder(route.query.orderId, { payment_method: selectedPaymentMethod.value })
      ElMessage.success('订单支付成功')
    } else {
      // 正常创建订单
      const orderData = {
        items: cartItems.value.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        })),
        address_id: selectedAddressId.value,
        remark: remark.value
      }

      const response = await orderApi.createOrder(orderData)
      
      // 如果选择了支付方式，直接支付订单
      if (selectedPaymentMethod.value) {
        await orderApi.payOrder(response.id, { payment_method: selectedPaymentMethod.value })
        ElMessage.success('订单支付成功')
      } else {
        ElMessage.success('订单提交成功')
      }
      
      try {
        await cartApi.clearCart()
      } catch (err) {
        console.error('清空购物车失败:', err)
      }
    }
    
    router.push({ name: 'Orders' })
  } catch (err) {
    console.error('提交订单失败:', err)
    ElMessage.error(err.response?.data?.message || '提交订单失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const goToAddressBook = () => {
  router.push({ name: 'AddressBook' })
}

onMounted(async () => {
  await initCartItems()
  if (cartItems.value.length === 0) {
    ElMessage.warning('购物车是空的')
    router.push({ name: 'Cart' })
    return
  }
  fetchAddresses()
})
</script>

<template>
  <div class="checkout-page">
    <div class="page-header">
      <button class="back-btn" @click="router.go(-1)">
        <span>←</span>
      </button>
      <h1 class="page-title">确认订单</h1>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else>
      <div class="address-section">
        <div class="section-header">
          <span class="section-title">收货地址</span>
          <button class="manage-btn" @click="goToAddressBook">
            管理地址
          </button>
        </div>
        <div v-if="addresses.length === 0" class="no-address">
          <p>暂无收货地址</p>
          <button class="add-address-btn" @click="goToAddressBook">
            添加地址
          </button>
        </div>
        <div v-else class="address-list">
          <div 
            v-for="address in addresses" 
            :key="address.id"
            class="address-item"
            :class="{ selected: address.id === selectedAddressId }"
            @click="selectedAddressId = address.id"
          >
            <div class="address-radio">
              <div class="radio" :class="{ checked: address.id === selectedAddressId }"></div>
            </div>
            <div class="address-info">
              <div class="address-header">
                <span class="name">{{ address.name }}</span>
                <span class="phone">{{ address.phone }}</span>
                <span v-if="address.is_default" class="default-tag">默认</span>
              </div>
              <div class="address-detail">
                {{ address.province }}{{ address.city }}{{ address.district }}{{ address.address }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="goods-section">
        <div class="section-header">
          <span class="section-title">商品信息</span>
        </div>
        <div class="goods-list">
          <div v-for="item in cartItems" :key="item.id" class="goods-item">
            <div class="item-image">
              <img :src="getProductImage(item)" :alt="item.product_name" />
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.product_name }}</div>
              <div class="item-meta">
                <span class="price">¥{{ formatPrice(item.price) }}</span>
                <span class="quantity">× {{ item.quantity }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="remark-section">
        <div class="section-header">
          <span class="section-title">订单备注</span>
        </div>
        <textarea 
          v-model="remark" 
          class="remark-input" 
          placeholder="选填，可以告诉卖家您的特殊需求"
          rows="3"
        ></textarea>
      </div>

      <div class="payment-section">
        <div class="section-header">
          <span class="section-title">支付方式</span>
        </div>
        <div class="payment-options">
          <div 
            v-for="method in paymentMethods" 
            :key="method.value"
            class="payment-option"
            :class="{ selected: selectedPaymentMethod === method.value }"
            @click="selectedPaymentMethod = method.value"
          >
            <div class="payment-radio">
              <div class="radio" :class="{ checked: selectedPaymentMethod === method.value }"></div>
            </div>
            <div class="payment-label">{{ method.label }}</div>
          </div>
        </div>
      </div>

      <div class="summary-section">
        <div class="summary-row">
          <span class="label">商品数量</span>
          <span class="value">{{ totalQuantity }} 件</span>
        </div>
        <div class="summary-row">
          <span class="label">运费</span>
          <span class="value">¥0.00</span>
        </div>
        <div class="summary-row total">
          <span class="label">实付金额</span>
          <span class="value total-price">¥{{ formatPrice(totalPrice) }}</span>
        </div>
      </div>

      <div class="submit-section">
        <div class="submit-content">
          <div class="submit-summary">
            <span class="label">合计：</span>
            <span class="price">¥{{ formatPrice(totalPrice) }}</span>
          </div>
          <button 
            class="submit-btn" 
            @click="handleSubmitOrder"
            :disabled="submitting || !selectedAddressId"
          >
            {{ submitting ? '提交中...' : (selectedPaymentMethod ? '支付订单' : '提交订单') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-page {
  padding: 16px;
  padding-bottom: 120px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: white;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.manage-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: #3b82f6;
  font-size: 14px;
  cursor: pointer;
}

.address-section,
.goods-section,
.remark-section,
.summary-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.no-address {
  text-align: center;
  padding: 20px;
  color: #6b7280;
}

.no-address p {
  margin: 0 0 12px 0;
}

.add-address-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.address-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.address-item.selected {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.address-radio {
  margin-right: 12px;
  padding-top: 2px;
}

.radio {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  transition: all 0.2s;
}

.radio.checked {
  border-color: #3b82f6;
  background: #3b82f6;
  position: relative;
}

.radio.checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}

.address-info {
  flex: 1;
  min-width: 0;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.address-header .name {
  font-weight: 600;
  color: #1f2937;
  font-size: 15px;
}

.address-header .phone {
  color: #6b7280;
  font-size: 14px;
}

.default-tag {
  background: #3b82f6;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.address-detail {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.4;
}

.goods-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.goods-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.goods-item:last-child {
  border-bottom: none;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 12px;
  flex-shrink: 0;
  background: #f9fafb;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  color: #1f2937;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-meta .price {
  font-size: 16px;
  font-weight: 600;
  color: #ef4444;
}

.item-meta .quantity {
  font-size: 14px;
  color: #6b7280;
}

.remark-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  transition: all 0.2s;
}

.remark-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.payment-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.payment-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-option {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.payment-option.selected {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.payment-radio {
  margin-right: 12px;
}

.payment-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  color: #6b7280;
}

.summary-row.total {
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
  margin-top: 4px;
}

.summary-row .label {
  color: #6b7280;
}

.summary-row.total .label {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.summary-row .value {
  color: #374151;
}

.summary-row.total .total-price {
  font-size: 20px;
  font-weight: 600;
  color: #ef4444;
}

.submit-section {
  position: fixed;
  bottom: 60px; /* 导航栏高度 */
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  z-index: 999;
  padding: 12px 16px;
}

.submit-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 480px;
  margin: 0 auto;
}

.submit-summary {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.submit-summary .label {
  font-size: 14px;
  color: #6b7280;
}

.submit-summary .price {
  font-size: 22px;
  font-weight: 600;
  color: #ef4444;
}

.submit-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.submit-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@media (min-width: 768px) {
  .checkout-page {
    max-width: 480px;
    margin: 0 auto;
  }
  
  .submit-section {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 12px 12px 0 0;
  }
}
</style>
