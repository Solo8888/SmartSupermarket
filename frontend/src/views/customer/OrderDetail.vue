<template>
  <div class="order-detail">
    <div class="header">
      <h1 class="title">订单详情</h1>
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span> 返回
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="!order" class="error">
      <p>订单不存在</p>
    </div>
    
    <div v-else class="order-content">
      <!-- 订单基本信息 -->
      <div class="order-info">
        <div class="order-header">
          <span class="order-id">订单号: {{ order.order_no || order.orderNo }}</span>
          <span class="order-status" :class="getStatusClass(order.status)">
            {{ getStatusText(order.status) }}
          </span>
        </div>
        <div class="order-meta">
          <span>创建时间: {{ formatDateTime(order.created_at || order.createdAt) }}</span>
          <span v-if="order.payment_time">支付时间: {{ formatDateTime(order.payment_time || order.paymentTime) }}</span>
        </div>
      </div>
      
      <!-- 收货信息 -->
      <div class="shipping-info">
        <h3 class="section-title">收货信息</h3>
        <div class="info-item">
          <span class="label">收货人:</span>
          <span class="value">{{ order.contact_name || order.contactName }}</span>
        </div>
        <div class="info-item">
          <span class="label">联系电话:</span>
          <span class="value">{{ order.contact_phone || order.contactPhone }}</span>
        </div>
        <div class="info-item">
          <span class="label">收货地址:</span>
          <span class="value">{{ order.shipping_address || order.shippingAddress }}</span>
        </div>
      </div>
      
      <!-- 商品列表 -->
      <div class="order-items">
        <h3 class="section-title">商品信息</h3>
        <div v-for="item in order.items" :key="item.id" class="order-item">
          <div class="item-image">
            <img :src="getProductImage(item)" :alt="item.product_name || item.productName" />
          </div>
          <div class="item-info">
            <div class="item-name">{{ item.product_name || item.productName }}</div>
            <div class="item-meta">
              <span>¥{{ formatPrice(item.price) }}</span>
              <span>× {{ item.quantity }}</span>
            </div>
          </div>
          <div class="item-subtotal">
            ¥{{ formatPrice(item.subtotal) }}
          </div>
        </div>
      </div>
      
      <!-- 金额信息 -->
      <div class="order-amount">
        <h3 class="section-title">金额信息</h3>
        <div class="amount-item">
          <span class="label">商品总额:</span>
          <span class="value">¥{{ formatPrice(order.total_amount || order.totalAmount) }}</span>
        </div>
        <div class="amount-item">
          <span class="label">优惠金额:</span>
          <span class="value">¥{{ formatPrice(order.discount_amount || order.discountAmount) }}</span>
        </div>
        <div class="amount-item total">
          <span class="label">实付金额:</span>
          <span class="value">¥{{ formatPrice(order.final_amount || order.finalAmount) }}</span>
        </div>
        <div v-if="order.payment_method" class="amount-item">
          <span class="label">支付方式:</span>
          <span class="value">{{ getPaymentMethodText(order.payment_method || order.paymentMethod) }}</span>
        </div>
      </div>
      
      <!-- 订单备注 -->
      <div v-if="order.remark" class="order-remark">
        <h3 class="section-title">订单备注</h3>
        <p>{{ order.remark }}</p>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-section">
        <button 
          v-if="order.status === 'delivered' " 
          class="action-btn review-btn"
          @click="navigateToReview(order)"
        >
          评价订单
        </button>
        <button 
          class="action-btn back-btn"
          @click="goBack"
        >
          返回列表
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as orderApi from '../../api/order'

const route = useRoute()
const router = useRouter()

const orderId = route.params.id
const order = ref(null)
const loading = ref(true)

const goBack = () => {
  router.back()
}

const navigateToReview = (order) => {
  router.push({
    name: 'OrderReview',
    params: { id: order.id }
  })
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getProductImage = (item) => {
  const productName = item.product_name || item.productName || '商品'
  if (item.product_image || item.productImage) {
    const imageUrl = item.product_image || item.productImage
    if (imageUrl.startsWith('http')) {
      return imageUrl
    }
    return window.location.origin + imageUrl
  }
  return `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(productName)}&image_size=square`
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待支付',
    'paid': '待发货',
    'shipped': '待收货',
    'delivered': '已收货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'pending': 'pending',
    'paid': 'paid',
    'shipped': 'shipped',
    'delivered': 'delivered',
    'completed': 'completed',
    'cancelled': 'cancelled'
  }
  return classMap[status] || ''
}

const getPaymentMethodText = (method) => {
  const methodMap = {
    'wechat': '微信支付',
    'alipay': '支付宝',
    'cash': '现金',
    'card': '银行卡'
  }
  return methodMap[method] || method
}

const loadOrder = async () => {
  loading.value = true
  try {
    const response = await orderApi.getOrder(orderId)
    order.value = response
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.order-detail {
  padding: 16px;
  padding-bottom: 80px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  flex: 1;
  text-align: center;
}

.back-btn {
  position: absolute;
  left: 0;
  background: none;
  border: none;
  font-size: 16px;
  color: #1890ff;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.back-icon {
  margin-right: 4px;
  font-size: 20px;
}

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.order-content {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.order-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.order-id {
  font-size: 14px;
  color: #666;
}

.order-status {
  font-size: 14px;
  font-weight: 500;
}

.order-status.pending {
  color: #faad14;
}

.order-status.paid {
  color: #1890ff;
}

.order-status.shipped {
  color: #722ed1;
}

.order-status.delivered {
  color: #13c2c2;
}

.order-status.completed {
  color: #52c41a;
}

.order-status.cancelled {
  color: #999;
}

.order-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #999;
}

.shipping-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  width: 80px;
  color: #666;
  flex-shrink: 0;
}

.info-item .value {
  flex: 1;
  color: #333;
}

.order-items {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.order-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-name {
  font-size: 14px;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.item-subtotal {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  flex-shrink: 0;
}

.order-amount {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.amount-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.amount-item .label {
  color: #666;
}

.amount-item .value {
  color: #333;
}

.amount-item.total {
  font-weight: 600;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.amount-item.total .value {
  color: #ff4d4f;
  font-size: 16px;
}

.order-remark {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.order-remark p {
  font-size: 14px;
  color: #333;
  margin: 0;
  line-height: 1.5;
}

.action-section {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  min-width: 120px;
}

.review-btn {
  background-color: #722ed1;
  color: white;
}

.review-btn:hover {
  background-color: #873bf0;
}

.action-section .back-btn {
  position: static;
  background-color: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}

.action-section .back-btn:hover {
  background-color: #e6f7ff;
}

@media (min-width: 768px) {
  .order-detail {
    max-width: 480px;
    margin: 0 auto;
  }
}
</style>