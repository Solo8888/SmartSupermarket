<script setup>
import { ref, onMounted } from 'vue'
import * as inventoryApi from '../../api/inventory'
import * as productApi from '../../api/product'

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

const formData = ref({
  stock_quantity: 0,
  warning_quantity: 10
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
    inventories.value = response.data || []
    total.value = response.data.total || 0
  } catch (err) {
    console.error('获取库存失败:', err)
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
    products.value = response.data || []
  } catch (err) {
    console.error('获取商品失败:', err)
  }
}

const getProductName = (productId) => {
  if (!products.value || products.value.length === 0) {
    return `商品 #${productId}`
  }
  const product = products.value.find(p => p.id === productId)
  return product ? product.name : `商品 #${productId}`
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
    stock_quantity: inventory.stock_quantity,
    warning_quantity: inventory.warning_quantity
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
    } else if (modalType.value === 'stock-in') {
      await inventoryApi.stockIn(currentInventory.value.product_id, stockFormData.value)
    } else if (modalType.value === 'stock-out') {
      await inventoryApi.stockOut(currentInventory.value.product_id, stockFormData.value)
    }
    showModal.value = false
    fetchInventories()
  } catch (err) {
    console.error('操作失败:', err)
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
      <div class="header-right">
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
                  <th>商品ID</th>
                  <th>商品名称</th>
                  <th>库存数量</th>
                  <th>预警数量</th>
                  <th>状态</th>
                  <th>最后更新</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inventory in inventories" :key="inventory.id">
                  <td>{{ inventory.product_id }}</td>
                  <td class="product-name">{{ getProductName(inventory.product_id) }}</td>
                  <td class="stock-quantity">{{ inventory.stock_quantity }}</td>
                  <td>{{ inventory.warning_quantity }}</td>
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
    
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h4>{{ getModalTitle() }}</h4>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
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
          
          <div v-if="modalType === 'update'" class="form-group">
            <label>预警数量</label>
            <input v-model.number="formData.warning_quantity" type="number" min="0" placeholder="请输入预警数量" />
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
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">确定</button>
        </div>
      </div>
    </div>
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

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
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

.page-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 20px;
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

.stock-quantity {
  font-weight: 600;
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
  max-width: 480px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
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
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
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
