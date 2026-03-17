<script setup>
import { ref, onMounted } from 'vue'
import * as storeApi from '../../api/store'
import { ElDialog } from 'element-plus'

const stores = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const currentStore = ref(null)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formData = ref({
  name: '',
  address: '',
  phone: '',
  opening_hours: '',
  status: 'active'
})

const statusOptions = [
  { label: '激活', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

const fetchStores = async () => {
  loading.value = true
  try {
    const response = await storeApi.getStores({
      page: page.value,
      size: pageSize.value
    })
    stores.value = response.items || []
    total.value = response.total || 0
  } catch (err) {
    console.error('获取门店列表失败:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEdit.value = false
  currentStore.value = null
  formData.value = {
    name: '',
    address: '',
    phone: '',
    opening_hours: '',
    status: 'active'
  }
  showModal.value = true
}

const openEditModal = (store) => {
  isEdit.value = true
  currentStore.value = store
  formData.value = {
    name: store.name,
    address: store.address,
    phone: store.phone,
    opening_hours: store.opening_hours,
    status: store.status
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await storeApi.updateStore(currentStore.value.id, formData.value)
    } else {
      await storeApi.createStore(formData.value)
    }
    showModal.value = false
    fetchStores()
  } catch (err) {
    console.error('操作失败:', err)
  }
}

const handleDelete = async (store) => {
  if (!confirm(`确定要删除门店"${store.name}"吗？`)) {
    return
  }
  try {
    await storeApi.deleteStore(store.id)
    fetchStores()
  } catch (err) {
    console.error('删除失败:', err)
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchStores()
}

onMounted(() => {
  fetchStores()
})
</script>

<template>
  <div class="stores-page">
    <div class="page-header">
      <div class="header-left">
        <h3>门店管理</h3>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="openCreateModal">
          + 添加门店
        </button>
      </div>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>门店名称</th>
              <th>地址</th>
              <th>联系电话</th>
              <th>营业时间</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="store in stores" :key="store.id">
              <td>{{ store.name }}</td>
              <td>{{ store.address }}</td>
              <td>{{ store.phone }}</td>
              <td>{{ store.opening_hours }}</td>
              <td>
                <span class="status-badge" :class="store.status">
                  {{ store.status === 'active' ? '激活' : '禁用' }}
                </span>
              </td>
              <td>{{ new Date(store.created_at).toLocaleString() }}</td>
              <td class="action-buttons">
                <button class="btn btn-sm btn-primary" @click="openEditModal(store)">
                  编辑
                </button>
                <button class="btn btn-sm btn-danger" @click="handleDelete(store)">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="stores.length === 0" class="empty">
          暂无门店，点击上方按钮添加
        </div>
        
        <div v-if="total > 0" class="pagination">
          <button 
            class="btn btn-sm btn-secondary" 
            @click="handlePageChange(page - 1)" 
            :disabled="page === 1"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ page }} 页，共 {{ Math.ceil(total / pageSize) }} 页
          </span>
          <button 
            class="btn btn-sm btn-secondary" 
            @click="handlePageChange(page + 1)" 
            :disabled="page * pageSize >= total"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
    
    <ElDialog
      v-model="showModal"
      :title="isEdit ? '编辑门店' : '添加门店'"
      width="480px"
      center
    >
      <div class="modal-body">
        <div class="form-group">
          <label>门店名称 <span class="required">*</span></label>
          <input v-model="formData.name" type="text" placeholder="请输入门店名称" />
        </div>
        <div class="form-group">
          <label>地址 <span class="required">*</span></label>
          <textarea v-model="formData.address" placeholder="请输入门店地址"></textarea>
        </div>
        <div class="form-group">
          <label>联系电话 <span class="required">*</span></label>
          <input v-model="formData.phone" type="text" placeholder="请输入联系电话" />
        </div>
        <div class="form-group">
          <label>营业时间 <span class="required">*</span></label>
          <input v-model="formData.opening_hours" type="text" placeholder="请输入营业时间" />
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="formData.status">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </button>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.stores-page {
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

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex: 1;
  overflow: auto;
}

.loading, .empty {
  padding: 60px 20px;
  text-align: center;
  color: #9ca3af;
}

.table-container {
  padding: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.data-table th, .data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.data-table tr:hover {
  background-color: #f9fafb;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #059669;
}

.status-badge.inactive {
  background-color: #fef2f2;
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
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

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.page-info {
  color: #6b7280;
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

.form-group label .required {
  color: #ef4444;
  margin-left: 4px;
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
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.dialog-footer {
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
  
  .table-container {
    padding: 12px;
  }
  
  .data-table th, .data-table td {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .action-buttons {
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
}
</style>
