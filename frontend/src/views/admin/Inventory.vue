<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElDialog } from 'element-plus'
import * as inventoryApi from '../../api/inventory'
import * as productApi from '../../api/product'

const activeTab = ref('inventory')
const inventories = ref([])
const products = ref([])
const loading = ref(false)
const showModal = ref(false)
const modalType = ref('')
const currentInventory = ref(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const searchQuery = ref('')

// 库存优化相关数据
const replenishmentSuggestions = ref([])
const transferPlans = ref([])
const optimizationLoading = ref(false)
const selectedProductId = ref('')
const thresholdForm = ref({
  warning_quantity: 10
})
const showThresholdModal = ref(false)
const currentProduct = ref(null)

const formData = ref({
  stock_quantity: 0
})

const stockFormData = ref({
  quantity: 0,
  remark: ''
})

const fetchInventories = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await inventoryApi.getInventories(params)
    inventories.value = response.items || []
    total.value = response.total || 0
  } catch (err) {
    console.error('获取库存失败:', err)
    ElMessage.error('获取库存失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchInventories()
}

const clearSearch = () => {
  searchQuery.value = ''
  page.value = 1
  fetchInventories()
}

const fetchProducts = async () => {
  try {
    const response = await productApi.getAllProducts()
    products.value = response || []
  } catch (err) {
    console.error('获取商品失败:', err)
    ElMessage.error('获取商品失败，请稍后重试')
  }
}

const getProductName = (productId) => {
  if (!products.value || products.value.length === 0) {
    return `商品 #${productId}`
  }
  const product = products.value.find(p => p.id === productId)
  return product ? product.name : `商品 #${productId}`
}

const getProductImage = (productId) => {
  if (!products.value || products.value.length === 0) {
    return ''
  }
  const product = products.value.find(p => p.id === productId)
  if (product && product.image_url) {
    if (product.image_url.startsWith('http')) {
      return product.image_url
    }
    return window.location.origin + product.image_url
  }
  return ''
}

const getStockStatus = (inventory) => {
  if (inventory.stock_quantity <= 0) {
    return '缺货'
  } else if (inventory.stock_quantity <= inventory.warning_quantity) {
    return '预警'
  }
  return '正常'
}

const getStockStatusClass = (inventory) => {
  if (inventory.stock_quantity <= 0) {
    return 'out-of-stock'
  } else if (inventory.stock_quantity <= inventory.warning_quantity) {
    return 'warning'
  }
  return 'normal'
}

const openUpdateModal = (inventory) => {
  modalType.value = 'update'
  currentInventory.value = inventory
  formData.value = {
    stock_quantity: inventory.stock_quantity
  }
  showModal.value = true
}

const openStockInModal = (inventory) => {
  modalType.value = 'stock-in'
  currentInventory.value = inventory
  stockFormData.value = {
    quantity: 0,
    remark: ''
  }
  showModal.value = true
}

const openStockOutModal = (inventory) => {
  modalType.value = 'stock-out'
  currentInventory.value = inventory
  stockFormData.value = {
    quantity: 0,
    remark: ''
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (modalType.value === 'update') {
      await inventoryApi.updateInventory(currentInventory.value.product_id, formData.value)
      ElMessage.success('更新库存成功')
    } else if (modalType.value === 'stock-in') {
      await inventoryApi.stockIn(currentInventory.value.product_id, stockFormData.value)
      ElMessage.success('入库登记成功')
    } else if (modalType.value === 'stock-out') {
      await inventoryApi.stockOut(currentInventory.value.product_id, stockFormData.value)
      ElMessage.success('出库审核成功')
    }
    showModal.value = false
    fetchInventories()
  } catch (err) {
    console.error('操作失败:', err)
    ElMessage.error(err.response?.data?.message || '操作失败，请稍后重试')
  }
}

const getModalTitle = () => {
  const titleMap = {
    'update': '更新库存',
    'stock-in': '入库登记',
    'stock-out': '出库审核'
  }
  return titleMap[modalType.value] || '操作'
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchInventories()
}

// 库存优化功能
const fetchReplenishmentSuggestions = async () => {
  optimizationLoading.value = true
  try {
    const response = await inventoryApi.getReplenishmentSuggestions()
    replenishmentSuggestions.value = response.suggestions || []
  } catch (err) {
    console.error('获取补货建议失败:', err)
    ElMessage.error('获取补货建议失败，请稍后重试')
  } finally {
    optimizationLoading.value = false
  }
}

const fetchTransferPlans = async () => {
  optimizationLoading.value = true
  try {
    const params = {}
    if (selectedProductId.value) {
      params.product_id = selectedProductId.value
    }
    const response = await inventoryApi.getTransferPlans(params)
    transferPlans.value = response.transfer_plans || []
  } catch (err) {
    console.error('获取调拨方案失败:', err)
    ElMessage.error('获取调拨方案失败，请稍后重试')
  } finally {
    optimizationLoading.value = false
  }
}

const openThresholdModal = (product) => {
  currentProduct.value = product
  thresholdForm.value = {
    warning_quantity: product.warning_quantity || 10
  }
  showThresholdModal.value = true
}

const handleUpdateThreshold = async () => {
  try {
    await inventoryApi.updateThreshold(currentProduct.value.id, thresholdForm.value)
    ElMessage.success('预警阈值更新成功')
    showThresholdModal.value = false
    fetchInventories()
  } catch (err) {
    console.error('更新预警阈值失败:', err)
    ElMessage.error(err.response?.data?.message || '更新预警阈值失败，请稍后重试')
  }
}

const handleTabChange = (tab) => {
  activeTab.value = tab
  if (tab === 'replenishment') {
    fetchReplenishmentSuggestions()
  } else if (tab === 'transfer') {
    fetchTransferPlans()
  }
}

onMounted(() => {
  fetchInventories()
  fetchProducts()
})
</script>

<template>
  <div class="inventory-page">
    <div class="page-header">
      <div class="header-left">
        <h3>库存管理</h3>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="tabs-nav">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'inventory' }"
        @click="handleTabChange('inventory')"
      >
        库存明细
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'replenishment' }"
        @click="handleTabChange('replenishment')"
      >
        补货建议
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'transfer' }"
        @click="handleTabChange('transfer')"
      >
        调拨方案
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'threshold' }"
        @click="handleTabChange('threshold')"
      >
        预警阈值设置
      </button>
    </div>

    <!-- 库存明细标签页 -->
    <div v-if="activeTab === 'inventory'" class="tab-content">
      <div class="content-header">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索商品名称、品牌、条码"
            @keyup.enter="handleSearch"
          />
          <button v-if="searchQuery" class="clear-search-btn" @click="clearSearch">×</button>
          <button class="btn btn-secondary search-btn" @click="handleSearch">搜索</button>
        </div>
      </div>

      <div class="content-card">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else>
          <div v-if="inventories.length === 0" class="empty">
            暂无库存数据
          </div>
          <div v-else>
            <div class="table-wrapper">
              <table class="inventory-table">
                <thead>
                  <tr>
                    <th>商品图片</th>
                    <th>商品名称</th>
                    <th>库存数量</th>
                    <th>状态</th>
                    <th>最后更新</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="inventory in inventories" :key="inventory.id">
                    <td>
                      <div class="product-image">
                        <img v-if="getProductImage(inventory.product_id)" :src="getProductImage(inventory.product_id)" :alt="getProductName(inventory.product_id)" />
                        <span v-else class="no-image">无图片</span>
                      </div>
                    </td>
                    <td class="product-name">{{ getProductName(inventory.product_id) }}</td>
                    <td class="stock-quantity">{{ inventory.stock_quantity }}</td>
                    <td>
                      <span class="status-badge" :class="getStockStatusClass(inventory)">
                        {{ getStockStatus(inventory) }}
                      </span>
                    </td>
                    <td>{{ new Date(inventory.last_stock_time).toLocaleString() }}</td>
                    <td>
                      <div class="actions">
                        <button class="btn-sm btn-secondary" @click="openUpdateModal(inventory)">
                          编辑
                        </button>
                        <button class="btn-sm btn-success" @click="openStockInModal(inventory)">
                          入库
                        </button>
                        <button class="btn-sm btn-warning" @click="openStockOutModal(inventory)">
                          出库
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
    </div>

    <!-- 补货建议标签页 -->
    <div v-if="activeTab === 'replenishment'" class="tab-content">
      <div class="content-card">
        <div v-if="optimizationLoading" class="loading">加载中...</div>
        <div v-else>
          <div v-if="replenishmentSuggestions.length === 0" class="empty">
            暂无需补货的商品
          </div>
          <div v-else>
            <div class="table-wrapper">
              <table class="inventory-table">
                <thead>
                  <tr>
                    <th>商品名称</th>
                    <th>当前库存</th>
                    <th>安全库存</th>
                    <th>建议补货量</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="suggestion in replenishmentSuggestions" :key="suggestion.product_id">
                    <td class="product-name">{{ suggestion.product_name }}</td>
                    <td>{{ suggestion.current_stock }}</td>
                    <td>{{ suggestion.safety_stock }}</td>
                    <td class="highlight">{{ suggestion.suggested_replenishment }}</td>
                    <td>
                      <button class="btn-sm btn-primary">生成采购单</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 调拨方案标签页 -->
    <div v-if="activeTab === 'transfer'" class="tab-content">
      <div class="content-header">
        <div class="filter-box">
          <select v-model="selectedProductId" @change="fetchTransferPlans">
            <option value="">所有商品</option>
            <option v-for="product in products" :key="product.id" :value="product.id">
              {{ product.name }}
            </option>
          </select>
          <button class="btn btn-secondary" @click="fetchTransferPlans">刷新</button>
        </div>
      </div>

      <div class="content-card">
        <div v-if="optimizationLoading" class="loading">加载中...</div>
        <div v-else>
          <div v-if="transferPlans.length === 0" class="empty">
            暂无需调拨的商品
          </div>
          <div v-else>
            <div class="table-wrapper">
              <table class="inventory-table">
                <thead>
                  <tr>
                    <th>商品名称</th>
                    <th>调出门店</th>
                    <th>调入门店</th>
                    <th>调拨数量</th>
                    <th>调拨原因</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="plan in transferPlans" :key="`${plan.product_id}-${plan.from_store_id}-${plan.to_store_id}`">
                    <td class="product-name">{{ plan.product_name }}</td>
                    <td>{{ plan.from_store_name }}</td>
                    <td>{{ plan.to_store_name }}</td>
                    <td class="highlight">{{ plan.transfer_quantity }}</td>
                    <td>{{ plan.reason }}</td>
                    <td>
                      <button class="btn-sm btn-primary">执行调拨</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预警阈值设置标签页 -->
    <div v-if="activeTab === 'threshold'" class="tab-content">
      <div class="content-card">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else>
          <div v-if="inventories.length === 0" class="empty">
            暂无库存数据
          </div>
          <div v-else>
            <div class="table-wrapper">
              <table class="inventory-table">
                <thead>
                  <tr>
                    <th>商品图片</th>
                    <th>商品名称</th>
                    <th>当前库存</th>
                    <th>预警阈值</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="inventory in inventories" :key="inventory.id">
                    <td>
                      <div class="product-image">
                        <img v-if="getProductImage(inventory.product_id)" :src="getProductImage(inventory.product_id)" :alt="getProductName(inventory.product_id)" />
                        <span v-else class="no-image">无图片</span>
                      </div>
                    </td>
                    <td class="product-name">{{ getProductName(inventory.product_id) }}</td>
                    <td>{{ inventory.stock_quantity }}</td>
                    <td>{{ inventory.warning_quantity }}</td>
                    <td>
                      <span class="status-badge" :class="getStockStatusClass(inventory)">
                        {{ getStockStatus(inventory) }}
                      </span>
                    </td>
                    <td>
                      <button class="btn-sm btn-secondary" @click="openThresholdModal({ id: inventory.product_id, name: getProductName(inventory.product_id), warning_quantity: inventory.warning_quantity })">
                        设置阈值
                      </button>
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
    </div>

    <!-- 库存操作弹窗 -->
    <ElDialog
      v-model="showModal"
      :title="getModalTitle()"
      width="480px"
      center
    >
      <div class="modal-body">
        <div class="product-info">
          <p><strong>商品ID:</strong> {{ currentInventory?.product_id }}</p>
          <p><strong>商品名称:</strong> {{ getProductName(currentInventory?.product_id) }}</p>
          <p><strong>当前库存:</strong> {{ currentInventory?.stock_quantity }}</p>
        </div>

        <div v-if="modalType === 'update'" class="form-group">
          <label>库存数量</label>
          <input v-model.number="formData.stock_quantity" type="number" min="0" placeholder="请输入库存数量" />
        </div>

        <div v-if="modalType === 'stock-in' || modalType === 'stock-out'" class="form-group">
          <label>数量</label>
          <input v-model.number="stockFormData.quantity" type="number" min="1" placeholder="请输入数量" />
        </div>

        <div v-if="modalType === 'stock-in' || modalType === 'stock-out'" class="form-group">
          <label>备注</label>
          <textarea v-model="stockFormData.remark" placeholder="请输入备注"></textarea>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">确定</button>
        </div>
      </template>
    </ElDialog>

    <!-- 预警阈值设置弹窗 -->
    <ElDialog
      v-model="showThresholdModal"
      title="设置库存预警阈值"
      width="480px"
      center
    >
      <div class="modal-body">
        <div class="product-info">
          <p><strong>商品ID:</strong> {{ currentProduct?.id }}</p>
          <p><strong>商品名称:</strong> {{ currentProduct?.name }}</p>
        </div>

        <div class="form-group">
          <label>预警阈值（安全库存）</label>
          <input v-model.number="thresholdForm.warning_quantity" type="number" min="0" placeholder="请输入预警阈值" />
          <p class="form-tip">当库存数量低于此值时，系统会发出预警提醒</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showThresholdModal = false">取消</button>
          <button class="btn btn-primary" @click="handleUpdateThreshold">确定</button>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.inventory-page {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 20px;
}

/* 标签页样式 */
.tabs-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #3b82f6;
}

.tab-btn.active {
  color: #3b82f6;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.search-box input {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  width: 280px;
  padding-right: 40px;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clear-search-btn {
  position: absolute;
  right: 90px;
  background: none;
  border: none;
  font-size: 18px;
  color: #9ca3af;
  cursor: pointer;
  padding: 0 8px;
  line-height: 1;
}

.clear-search-btn:hover {
  color: #6b7280;
}

.search-btn {
  padding: 10px 16px;
}

.filter-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-box select {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  min-width: 200px;
}

.filter-box select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

.inventory-table {
  width: 100%;
  border-collapse: collapse;
}

.inventory-table th,
.inventory-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.inventory-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.inventory-table td {
  color: #4b5563;
  font-size: 14px;
}

.product-name {
  font-weight: 500;
  color: #1f2937;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image .no-image {
  color: #9ca3af;
  font-size: 12px;
  text-align: center;
}

.stock-quantity {
  font-weight: 600;
  font-size: 16px;
}

.highlight {
  font-weight: 600;
  color: #dc2626;
  font-size: 16px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.normal {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.warning {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.out-of-stock {
  background-color: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 8px;
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

.btn-success {
  background-color: #d1fae5;
  color: #065f46;
}

.btn-success:hover {
  background-color: #a7f3d0;
}

.btn-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.btn-warning:hover {
  background-color: #fde68a;
}

.product-info {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.product-info p {
  margin: 8px 0;
  color: #374151;
  font-size: 14px;
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

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-tip {
  margin-top: 8px;
  color: #6b7280;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .tabs-nav {
    flex-wrap: wrap;
  }

  .tab-btn {
    padding: 10px 16px;
    font-size: 13px;
  }

  .table-wrapper {
    padding: 12px;
  }

  .inventory-table th,
  .inventory-table td {
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
}
</style>
