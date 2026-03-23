<template>
  <div class="orders-page">
    <div class="header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">我的订单</h1>
    </div>
    
    <div class="tab-bar">
      <div 
        v-for="tab in tabs" 
        :key="tab.value"
        class="tab-item"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="filteredOrders.length === 0" class="empty">
      <div class="empty-icon">📋</div>
      <p>暂无订单</p>
    </div>
    
    <div v-else class="order-list">
      <div v-for="order in filteredOrders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-id">订单号: {{ order.order_no || order.orderNo || order.id }}</span>
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
            </div>
          </div>
        </div>
        
        <div class="order-footer">
          <div class="order-total">
            共 {{ order.items?.length || 0 }} 件 合计: 
            <span class="total-price">¥{{ formatPrice(order.total_amount || order.totalAmount) }}</span>
          </div>
          <div class="order-actions">
            <button 
              v-if="order.status === 'pending' " 
              class="action-btn pay-btn"
              @click="payOrder(order)"
            >
              立即支付
            </button>
            <button 
              v-if="order.status === 'paid' " 
              class="action-btn confirm-btn"
              @click="simulateShip(order)"
            >
              模拟发货
            </button>
            <button 
              v-if="order.status === 'shipped' " 
              class="action-btn confirm-btn"
              @click="confirmOrder(order)"
            >
              确认收货
            </button>
            <button 
              v-if="order.status === 'delivered' " 
              class="action-btn review-btn"
              @click="navigateToReview(order)"
            >
              评价订单
            </button>
            <button 
              v-if="order.status === 'pending' || order.status === 'paid' " 
              class="action-btn cancel-btn"
              @click="cancelOrder(order)"
            >
              取消订单
            </button>
            <button 
              class="action-btn detail-btn"
              @click="viewOrderDetail(order)"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as orderApi from '../../api/order'

const router = useRouter()

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待支付', value: 'pending' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '待评价', value: 'review' },
  { label: '已完成', value: 'completed' }
]

const activeTab = ref('all')
const orders = ref([])
const loading = ref(false)

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') {
    return orders.value
  } else if (activeTab.value === 'review') {
    // 待评价标签显示已收货状态的订单
    return orders.value.filter(order => order.status === 'delivered')
  }
  return orders.value.filter(order => order.status === activeTab.value)
})

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

const loadOrders = async () => {
  loading.value = true
  try {
    const response = await orderApi.getOrders({ page: 1, size: 50 })
    console.log('订单列表响应:', response)
    if (response && typeof response === 'object') {
      orders.value = response.items || response.orders || response.data?.orders || []
    } else {
      orders.value = []
    }
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
    orders.value = []
  } finally {
    loading.value = false
  }
}

const payOrder = async (order) => {
  try {
    // 跳转到订单结算页面，带上订单ID
    router.push({
      name: 'OrderCheckout',
      query: { 
        orderId: order.id,
        payMode: 'true'
      }
    })
  } catch (error) {
    console.error('跳转到支付页面失败:', error)
    ElMessage.error('跳转到支付页面失败')
  }
}

const simulateShip = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确认发货？',
      '模拟发货',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.updateOrderStatus(order.id, { status: 'shipped' })
    ElMessage.success('发货成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发货失败:', error)
      ElMessage.error('发货失败')
    }
  }
}

const confirmOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      '确认已收到商品？',
      '确认收货',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.updateOrderStatus(order.id, { status: 'delivered' })
    ElMessage.success('确认收货成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
      ElMessage.error('确认收货失败')
    }
  }
}

const reviewOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      '订单评价功能开发中，先标记为已完成？',
      '评价订单',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.updateOrderStatus(order.id, { status: 'completed' })
    ElMessage.success('订单已完成')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const cancelOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确认取消订单 ${order.orderNo || order.id}？`,
      '取消订单',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.cancelOrder(order.id)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

const goBack = () => {
  router.push({
    name: 'Profile'
  })
}

const viewOrderDetail = (order) => {
  router.push({
    name: 'OrderDetail',
    params: { id: order.id }
  })
}

const navigateToReview = (order) => {
  router.push({
    name: 'OrderReview',
    params: { id: order.id }
  })
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-page {
  padding: 16px;
  padding-bottom: 80px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
}

.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #333;
  cursor: pointer;
  margin-right: 12px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.back-icon {
  font-size: 24px;
  line-height: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.tab-bar {
  display: flex;
  background-color: white;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tab-item {
  flex: 1;
  min-width: 60px;
  text-align: center;
  padding: 10px 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-item.active {
  background-color: #1890ff;
  color: white;
}

.loading,
.empty {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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
  gap: 12px;
  margin-bottom: 12px;
}

.order-item {
  display: flex;
  gap: 12px;
}

.item-image {
  width: 70px;
  height: 70px;
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
  justify-content: space-between;
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

.order-footer {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.order-total {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  text-align: right;
}

.total-price {
  font-size: 18px;
  font-weight: 600;
  color: #ff4d4f;
  margin-left: 4px;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.pay-btn {
  background-color: #ff4d4f;
  color: white;
}

.confirm-btn {
  background-color: #52c41a;
  color: white;
}

.review-btn {
  background-color: #722ed1;
  color: white;
}

.cancel-btn {
  background-color: white;
  color: #666;
  border: 1px solid #d9d9d9;
}

.detail-btn {
  background-color: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}

@media (min-width: 768px) {
  .orders-page {
    max-width: 480px;
    margin: 0 auto;
  }
}
</style>
