<script setup>
import { ref, onMounted } from 'vue'
import { promotionApi } from '../../api/promotion'

const promotions = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const currentPromotion = ref(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)

const formData = ref({
  name: '',
  description: '',
  type: 'discount',
  value: 0.1,
  start_time: '',
  end_time: '',
  status: 'draft'
})

const fetchPromotions = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    const response = await promotionApi.getPromotions(params)
    promotions.value = response.items || []
    total.value = response.total || 0
  } catch (err) {
    console.error('获取促销活动失败:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEdit.value = false
  currentPromotion.value = null
  formData.value = {
    name: '',
    description: '',
    type: 'discount',
    value: 0.1,
    start_time: '',
    end_time: '',
    status: 'draft'
  }
  showModal.value = true
}

const openEditModal = (promotion) => {
  isEdit.value = true
  currentPromotion.value = promotion
  formData.value = {
    name: promotion.name,
    description: promotion.description || '',
    type: promotion.type,
    value: promotion.value,
    start_time: formatDateTime(promotion.start_time),
    end_time: formatDateTime(promotion.end_time),
    status: promotion.status
  }
  showModal.value = true
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toISOString().slice(0, 16)
}

const handleSubmit = async () => {
  try {
    const payload = {
      ...formData.value,
      value: parseFloat(formData.value.value)
    }
    if (isEdit.value) {
      await promotionApi.updatePromotion(currentPromotion.value.id, payload)
    } else {
      await promotionApi.createPromotion(payload)
    }
    showModal.value = false
    fetchPromotions()
  } catch (err) {
    console.error('操作失败:', err)
  }
}

const handleDelete = async (promotion) => {
  if (!confirm(`确定要删除促销活动"${promotion.name}"吗？`)) {
    return
  }
  try {
    await promotionApi.deletePromotion(promotion.id)
    fetchPromotions()
  } catch (err) {
    console.error('删除失败:', err)
  }
}

const getTypeText = (type) => {
  const typeMap = {
    'discount': '折扣',
    'special_price': '特价',
    'buy_x_get_y': '买赠',
    'bundle': '套装'
  }
  return typeMap[type] || type
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'active': '进行中',
    'paused': '已暂停',
    'ended': '已结束'
  }
  return statusMap[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchPromotions()
}

onMounted(() => {
  fetchPromotions()
})
</script>

<template>
  <div class="promotions-page">
    <div class="page-header">
      <div class="header-left">
        <h3>促销活动管理</h3>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="openCreateModal()">
          + 添加促销活动
        </button>
      </div>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <div v-if="promotions.length === 0" class="empty">
          暂无促销活动，点击上方按钮添加
        </div>
        <div v-else>
          <div class="table-wrapper">
            <table class="promotion-table">
              <thead>
                <tr>
                  <th>活动名称</th>
                  <th>类型</th>
                  <th>促销值</th>
                  <th>开始时间</th>
                  <th>结束时间</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="promotion in promotions" :key="promotion.id">
                  <td class="promotion-name">{{ promotion.name }}</td>
                  <td>
                    <span class="type-badge">{{ getTypeText(promotion.type) }}</span>
                  </td>
                  <td>
                    {{ promotion.type === 'discount' ? promotion.value + '折' : '¥' + promotion.value }}
                  </td>
                  <td>{{ formatDate(promotion.start_time) }}</td>
                  <td>{{ formatDate(promotion.end_time) }}</td>
                  <td>
                    <span class="status-badge" :class="promotion.status">
                      {{ getStatusText(promotion.status) }}
                    </span>
                  </td>
                  <td>
                    <div class="actions">
                      <button class="btn-sm btn-secondary" @click="openEditModal(promotion)">
                        编辑
                      </button>
                      <button class="btn-sm btn-danger" @click="handleDelete(promotion)">
                        删除
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
          <h4>{{ isEdit ? '编辑促销活动' : '添加促销活动' }}</h4>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>活动名称 *</label>
            <input v-model="formData.name" type="text" placeholder="请输入促销活动名称" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>促销类型 *</label>
              <select v-model="formData.type">
                <option value="discount">折扣</option>
                <option value="special_price">特价</option>
                <option value="buy_x_get_y">买赠</option>
                <option value="bundle">套装</option>
              </select>
            </div>
            <div class="form-group">
              <label>促销值 *</label>
              <input v-model.number="formData.value" type="number" step="0.01" placeholder="请输入促销值" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>开始时间 *</label>
              <input v-model="formData.start_time" type="datetime-local" />
            </div>
            <div class="form-group">
              <label>结束时间 *</label>
              <input v-model="formData.end_time" type="datetime-local" />
            </div>
          </div>
          
          <div class="form-group">
            <label>状态</label>
            <select v-model="formData.status">
              <option value="draft">草稿</option>
              <option value="active">进行中</option>
              <option value="paused">已暂停</option>
              <option value="ended">已结束</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="formData.description" placeholder="请输入促销活动描述"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.promotions-page {
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

.promotion-table {
  width: 100%;
  border-collapse: collapse;
}

.promotion-table th,
.promotion-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.promotion-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.promotion-table td {
  color: #4b5563;
  font-size: 14px;
}

.promotion-name {
  font-weight: 500;
  color: #1f2937;
}

.type-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background-color: #dbeafe;
  color: #1d4ed8;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.draft {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.paused {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.ended {
  background-color: #e5e7eb;
  color: #4b5563;
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
  max-width: 640px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
  
  .promotion-table th,
  .promotion-table td {
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
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>
