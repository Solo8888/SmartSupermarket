<script setup>
import { ref, onMounted, computed } from 'vue'
import { orderApi } from '../../api/order'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const orders = ref([])
const loading = ref(false)
const showDetailModal = ref(false)
const showStatusModal = ref(false)
const showPayModal = ref(false)
const currentOrder = ref(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const statusFilter = ref('')

const selectedStatus = ref('')
const selectedPaymentMethod = ref('alipay')

const isCustomer = computed(() => userStore.user?.role === 'customer')
const isManager = computed(() => userStore.user?.role === 'inventory_manager' || userStore.user?.role === 'operations_manager')

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const response = await orderApi.getOrders(params)
    orders.value = response.items || []
    total.value = response.total || 0
  } catch (err) {
    console.error('获取订单失败:', err)
  } finally {
    loading.value = false
  }
}

const openDetailModal = async (order) => {
  try {
    const response = await orderApi.getOrder(order.id)
    currentOrder.value = response
    showDetailModal.value = true
  } catch (err) {
    console.error('获取订单详情失败:', err)
  }
}

const openStatusModal = (order) => {
  currentOrder.value = order
  selectedStatus.value = ''
  showStatusModal.value = true
}

const openPayModal = (order) => {
  currentOrder.value = order
  selectedPaymentMethod.value = 'alipay'
  showPayModal.value = true
}

const handleUpdateStatus = async () => {
  if (!selectedStatus.value) return
  try {
    await orderApi.updateOrderStatus(currentOrder.value.id, { status: selectedStatus.value })
    showStatusModal.value = false
    fetchOrders()
  } catch (err) {
    console.error('更新订单状态失败:', err)
  }
}

const handlePay = async () => {
  try {
    await orderApi.payOrder(currentOrder.value.id, { payment_method: selectedPaymentMethod.value })
    showPayModal.value = false
    fetchOrders()
  } catch (err) {
    console.error('支付订单失败:', err)
  }
}

const handleCancel = async (order) => {
  if (!confirm('确定要取消这个订单吗？')) {
    return
  }
  try {
    await orderApi.cancelOrder(order.id)
    fetchOrders()
  } catch (err) {
    console.error('取消订单失败:', err)
  }
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待支付',
    'paid': '已支付',
    'shipped': '已发货',
    'completed': '已完成',
    'cancelled': '已取消',
    'refunded': '已退款'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'pending': 'pending',
    'paid': 'paid',
    'shipped': 'shipped',
    'completed': 'completed',
    'cancelled': 'cancelled',
    'refunded': 'refunded'
  }
  return classMap[status] || ''
}

const getPaymentMethodText = (method) => {
  const methodMap = {
    'alipay': '支付宝',
    'wechat': '微信支付'
  }
  return methodMap[method] || method
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatPrice = (price) => {
  return '¥' + parseFloat(price).toFixed(2)
}

const canCancel = (order) => {
  return order.status === 'pending' || order.status === 'paid'
}

const canPay = (order) => {
  return order.status === 'pending' && isCustomer.value
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchOrders()
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="orders-page">
    <div class="page-header">
      <div class="header-left">
        <h3>订单管理</h3>
      </div>
      <div class="header-right">
        <select v-model="statusFilter" class="filter-select" @change="fetchOrders">
          <option value="">全部状态</option>
          <option value="pending">待支付</option>
          <option value="paid">已支付</option>
          <option value="shipped">已发货</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
      </div>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <div v-if="orders.length === 0" class="empty">
          暂无订单
        </div>
        <div v-else>
          <div class="table-wrapper">
            <table class="order-table">
              <thead>
                <tr>
                  <th>订单编号</th>
                  <th>金额</th>
                  <th>状态</th>
                  <th>支付方式</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in orders" :key="order.id">
                  <td class="order-no">{{ order.order_no }}</td>
                  <td class="order-amount">{{ formatPrice(order.final_amount) }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(order.status)">
                      {{ getStatusText(order.status) }}
                    </span>
                  </td>
                  <td>{{ getPaymentMethodText(order.payment_method) || '-' }}</td>
                  <td>{{ formatDate(order.created_at) }}</td>
                  <td>
                    <div class="actions">
                      <button class="btn-sm btn-secondary" @click="openDetailModal(order)">
                        详情
                      </button>
                      <button 
                        v-if="canPay(order)" 
                        class="btn-sm btn-primary" 
                        @click="openPayModal(order)"
                      >
                        支付
                      </button>
                      <button 
                        v-if="isManager" 
                        class="btn-sm btn-secondary" 
                        @click="openStatusModal(order)"
                      >
                        更新状态
                      </button>
                      <button 
                        v-if="canCancel(order)" 
                        class="btn-sm btn-danger" 
                        @click="handleCancel(order)"
                      >
                        取消
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="total > size" class="pagination">
            <button 
              class="btn btn-secondary" 
              :disabled="page <= 1"
              @click="handlePageChange(page - 1)"
            >
              上一页
            </button>
            <span class="page-info">
              第 {{ page }} 页 / 共 {{ Math.ceil(total / size) }} 页
            </span>
            <button 
              class="btn btn-secondary" 
              :disabled="page >= Math.ceil(total / size)"
              @click="handlePageChange(page + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
      <div class="modal detail-modal">
        <div class="modal-header">
          <h4>订单详情</h4>
          <button class="close-btn" @click="showDetailModal = false">×</button>
        </div>
        <div v-if="currentOrder" class="modal-body">
          <div class="order-info">
            <div class="info-row">
              <span class="label">订单编号:</span>
              <span class="value">{{ currentOrder.order_no }}</span>
            </div>
            <div class="info-row">
              <span class="label">订单状态:</span>
              <span class="value">
                <span class="status-badge" :class="getStatusClass(currentOrder.status)">
                  {{ getStatusText(currentOrder.status) }}
                </span>
              </span>
            </div>
            <div class="info-row">
              <span class="label">商品总额:</span>
              <span class="value">{{ formatPrice(currentOrder.total_amount) }}</span>
            </div>
            <div class="info-row">
              <span class="label">优惠金额:</span>
              <span class="value">-{{ formatPrice(currentOrder.discount_amount) }}</span>
            </div>
            <div class="info-row total">
              <span class="label">实付金额:</span>
              <span class="value">{{ formatPrice(currentOrder.final_amount) }}</span>
            </div>
            <div v-if="currentOrder.payment_method" class="info-row">
              <span class="label">支付方式:</span>
              <span class="value">{{ getPaymentMethodText(currentOrder.payment_method) }}</span>
            </div>
            <div v-if="currentOrder.payment_time" class="info-row">
              <span class="label">支付时间:</span>
              <span class="value">{{ formatDate(currentOrder.payment_time) }}</span>
            </div>
            <div v-if="currentOrder.shipping_address" class="info-row">
              <span class="label">收货地址:</span>
              <span class="value">{{ currentOrder.shipping_address }}</span>
            </div>
            <div v-if="currentOrder.contact_name" class="info-row">
              <span class="label">联系人:</span>
              <span class="value">{{ currentOrder.contact_name }}</span>
            </div>
            <div v-if="currentOrder.contact_phone" class="info-row">
              <span class="label">联系电话:</span>
              <span class="value">{{ currentOrder.contact_phone }}</span>
            </div>
            <div v-if="currentOrder.remark" class="info-row">
              <span class="label">备注:</span>
              <span class="value">{{ currentOrder.remark }}</span>
            </div>
          </div>
          
          <div v-if="currentOrder.items && currentOrder.items.length > 0" class="order-items">
            <h5>商品列表</h5>
            <div v-for="item in currentOrder.items" :key="item.id" class="order-item">
              <img v-if="item.product_image" :src="item.product_image.startsWith('http') ? item.product_image : window.location.origin + item.product_image" :alt="item.product_name" class="item-image" />
              <div class="item-info">
                <div class="item-name">{{ item.product_name }}</div>
                <div class="item-meta">
                  <span>{{ formatPrice(item.price) }} × {{ item.quantity }}</span>
                  <span class="item-subtotal">{{ formatPrice(item.subtotal) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
    
    <div v-if="showStatusModal" class="modal-overlay" @click.self="showStatusModal = false">
      <div class="modal">
        <div class="modal-header">
          <h4>更新订单状态</h4>
          <button class="close-btn" @click="showStatusModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择新状态</label>
            <select v-model="selectedStatus">
              <option value="">请选择</option>
              <option value="pending">待支付</option>
              <option value="paid">已支付</option>
              <option value="shipped">已发货</option>
              <option value="completed">已完成</option>
              <option value="cancelled">已取消</option>
              <option value="refunded">已退款</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showStatusModal = false">取消</button>
          <button class="btn btn-primary" @click="handleUpdateStatus">确认</button>
        </div>
      </div>
    </div>
    
    <div v-if="showPayModal" class="modal-overlay" @click.self="showPayModal = false">
      <div class="modal">
        <div class="modal-header">
          <h4>支付订单</h4>
          <button class="close-btn" @click="showPayModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="currentOrder" class="pay-info">
            <div class="pay-amount">
              <span class="label">支付金额:</span>
              <span class="amount">{{ formatPrice(currentOrder.final_amount) }}</span>
            </div>
            <div class="form-group">
              <label>选择支付方式</label>
              <div class="payment-methods">
                <label class="payment-option">
                  <input type="radio" v-model="selectedPaymentMethod" value="alipay" />
                  <span>支付宝</span>
                </label>
                <label class="payment-option">
                  <input type="radio" v-model="selectedPaymentMethod" value="wechat" />
                  <span>微信支付</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPayModal = false">取消</button>
          <button class="btn btn-primary" @click="handlePay">确认支付</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 20px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex: 1;
  overflow: auto;
}

.loading,
.empty {
  padding: 60px 20px;
  text-align: center;
  color: #9ca3af;
}

.table-wrapper {
  padding: 20px;
  overflow-x: auto;
}

.order-table {
  width: 100%;
  border-collapse: collapse;
}

.order-table th,
.order-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.order-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.order-table td {
  color: #4b5563;
  font-size: 14px;
}

.order-no {
  font-weight: 500;
  color: #1f2937;
  font-family: monospace;
}

.order-amount {
  font-weight: 600;
  color: #1f2937;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.paid {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.status-badge.shipped {
  background-color: #e0e7ff;
  color: #4338ca;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.cancelled {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-badge.refunded {
  background-color: #fee2e2;
  color: #dc2626;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #f3f4f6;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover {
  background-color: #fecaca;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.detail-modal {
  max-width: 720px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #6b7280;
}

.modal-body {
  padding: 24px;
}

.order-info {
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-row.total {
  border-bottom: none;
  padding-top: 16px;
  margin-top: 8px;
  border-top: 2px solid #f3f4f6;
}

.info-row .label {
  color: #6b7280;
  width: 100px;
  flex-shrink: 0;
}

.info-row .value {
  color: #1f2937;
  flex: 1;
}

.info-row.total .value {
  font-weight: 600;
  font-size: 18px;
  color: #dc2626;
}

.order-items h5 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 16px;
}

.order-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 8px;
  margin-bottom: 8px;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-name {
  color: #1f2937;
  font-weight: 500;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  color: #6b7280;
  font-size: 14px;
}

.item-subtotal {
  font-weight: 600;
  color: #1f2937;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-weight: 500;
  font-size: 14px;
}

.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
  background: white;
}

.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.pay-info {
  text-align: center;
}

.pay-amount {
  margin-bottom: 24px;
}

.pay-amount .label {
  display: block;
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
}

.pay-amount .amount {
  font-size: 32px;
  font-weight: 700;
  color: #dc2626;
}

.payment-methods {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #3b82f6;
}

.payment-option:has(input:checked) {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.payment-option input {
  margin: 0;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .table-wrapper {
    padding: 12px;
  }
  
  .order-table th,
  .order-table td {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .modal {
    margin: 16px;
    border-radius: 8px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
  
  .payment-methods {
    flex-direction: column;
  }
}
</style>
