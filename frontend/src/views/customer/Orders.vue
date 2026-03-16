<template>
  <div class="orders-page">
    <h1 class="page-title">我的订单</h1>
    
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
          <span class="order-id">订单号: {{ order.id }}</span>
          <span class="order-status" :class="getStatusClass(order.status)">
            {{ getStatusText(order.status) }}
          </span>
        </div>
        
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <div class="item-image">
              <img :src="getProductImage(item)" :alt="item.productName" />
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.productName }}</div>
              <div class="item-meta">
                <span>¥{{ formatPrice(item.price) }}</span>
                <span>× {{ item.quantity }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="order-footer">
          <div class="order-total">
            共 {{ order.items.length }} 件 合计: 
            <span class="total-price">¥{{ formatPrice(order.totalAmount) }}</span>
          </div>
          <div class="order-actions">
            <button 
              v-if="order.status === 'pending'" 
              class="action-btn pay-btn"
              @click="payOrder(order)"
            >
              立即支付
            </button>
            <button 
              v-if="order.status === 'pending' || order.status === 'paid'" 
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
import * as orderApi from '../../api/order'

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待支付', value: 'pending' },
  { label: '已支付', value: 'paid' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'completed' }
]

const activeTab = ref('all')
const orders = ref([])
const loading = ref(false)

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') {
    return orders.value
  }
  return orders.value.filter(order => order.status === activeTab.value)
})

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const getProductImage = (item) => {
  return `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(item.productName || '商品')}&image_size=square`
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待支付',
    'paid': '已支付',
    'shipped': '已发货',
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
    orders.value = response.data.orders || []
  } catch (error) {
    console.error('加载订单失败:', error)
    alert('加载订单失败')
  } finally {
    loading.value = false
  }
}

const payOrder = async (order) => {
  try {
    const confirmed = confirm(`确认支付订单 ${order.id}？金额: ¥${formatPrice(order.totalAmount)}`)
    if (!confirmed) return
    
    await orderApi.payOrder(order.id, { paymentMethod: 'alipay' })
    alert('支付成功')
    loadOrders()
  } catch (error) {
    console.error('支付失败:', error)
    alert('支付失败')
  }
}

const cancelOrder = async (order) => {
  try {
    const confirmed = confirm(`确认取消订单 ${order.id}？`)
    if (!confirmed) return
    
    await orderApi.cancelOrder(order.id)
    alert('订单已取消')
    loadOrders()
  } catch (error) {
    console.error('取消订单失败:', error)
    alert('取消订单失败')
  }
}

const viewOrderDetail = (order) => {
  alert('订单详情功能开发中...')
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

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
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
}

.action-btn {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.pay-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
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
</style>
