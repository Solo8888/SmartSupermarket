<template>
  <div class="order-review">
    <div class="header">
      <h1 class="title">订单评价</h1>
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
      <div class="order-info">
        <div class="order-header">
          <span class="order-id">订单号: {{ order.order_no || order.orderNo }}</span>
          <span class="order-status" :class="getStatusClass(order.status)">
            {{ getStatusText(order.status) }}
          </span>
        </div>
        
        <div class="order-items">
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
              
              <div class="review-section" v-if="order.status === 'delivered'">
                <div class="review-header">
                  <h3>评价商品</h3>
                </div>
                
                <div class="rating">
                  <span class="rating-label">评分:</span>
                  <div class="stars">
                    <span 
                      v-for="star in 5" 
                      :key="star"
                      class="star"
                      :class="{ active: reviewForm[item.id]?.rating >= star }"
                      @click="setRating(item.id, star)"
                    >
                      ★
                    </span>
                  </div>
                </div>
                
                <div class="review-content">
                  <textarea 
                    v-model="reviewForm[item.id].content" 
                    placeholder="请输入评价内容..."
                    class="review-textarea"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="order-total">
          共 {{ order.items?.length || 0 }} 件 合计: 
          <span class="total-price">¥{{ formatPrice(order.total_amount || order.totalAmount) }}</span>
        </div>
      </div>
      
      <div class="action-section" v-if="order.status === 'delivered'">
        <button 
          class="submit-btn"
          @click="submitReview"
          :disabled="!canSubmit"
        >
          提交评价
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as orderApi from '../../api/order'
import * as reviewApi from '../../api/review'

const route = useRoute()
const router = useRouter()

const orderId = route.params.id
const order = ref(null)
const loading = ref(true)
const reviewForm = reactive({})

const canSubmit = computed(() => {
  if (!order.value) return false
  
  const items = order.value.items || []
  for (const item of items) {
    if (!reviewForm[item.id] || !reviewForm[item.id].rating) {
      return false
    }
  }
  return true
})

const goBack = () => {
  router.back()
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
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

const setRating = (itemId, rating) => {
  if (!reviewForm[itemId]) {
    reviewForm[itemId] = {
      rating: rating,
      content: ''
    }
  } else {
    reviewForm[itemId].rating = rating
  }
}

const loadOrder = async () => {
  loading.value = true
  try {
    const response = await orderApi.getOrder(orderId)
    order.value = response
    
    // 检查订单状态
    if (order.value.status !== 'delivered') {
      ElMessage.error('只有已收货的订单才能评价')
      router.push('/customer/orders')
      return
    }
    
    // 初始化评价表单
    const items = order.value.items || []
    for (const item of items) {
      reviewForm[item.id] = {
        rating: 5, // 默认5星
        content: ''
      }
    }
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const submitReview = async () => {
  try {
    const items = order.value.items || []
    const reviewPromises = []
    
    for (const item of items) {
      const reviewData = {
        order_item_id: item.id,
        rating: reviewForm[item.id].rating,
        content: reviewForm[item.id].content
      }
      reviewPromises.push(reviewApi.createReview(reviewData))
    }
    
    await Promise.all(reviewPromises)
    ElMessage.success('评价提交成功')
    router.push('/customer/orders')
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交评价失败')
  }
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.order-review {
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

.order-info {
  margin-bottom: 20px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.order-id {
  font-size: 13px;
  color: #999;
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

.order-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.order-item {
  display: flex;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
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
  margin-top: auto;
}

.review-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.review-header {
  margin-bottom: 12px;
}

.review-header h3 {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  color: #333;
}

.rating {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.rating-label {
  font-size: 14px;
  color: #666;
  margin-right: 12px;
}

.stars {
  display: flex;
  gap: 8px;
}

.star {
  font-size: 20px;
  color: #d9d9d9;
  cursor: pointer;
  transition: color 0.2s;
}

.star.active {
  color: #faad14;
}

.review-content {
  margin-top: 8px;
}

.review-textarea {
  width: 100%;
  height: 100px;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.review-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.order-total {
  font-size: 14px;
  color: #666;
  text-align: right;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
  color: #ff4d4f;
  margin-left: 4px;
}

.action-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 24px;
  background-color: #1890ff;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 200px;
}

.submit-btn:hover {
  background-color: #40a9ff;
}

.submit-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

@media (min-width: 768px) {
  .order-review {
    max-width: 480px;
    margin: 0 auto;
  }
}
</style>
