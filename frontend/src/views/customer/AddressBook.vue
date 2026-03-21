<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElDialog } from 'element-plus'
import * as addressApi from '../../api/address'

const addresses = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const currentAddress = ref(null)

const formData = ref({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: '',
  is_default: false
})

const fetchAddresses = async () => {
  loading.value = true
  try {
    const response = await addressApi.getAddresses()
    console.log('获取地址列表响应:', response)
    // 确保addresses.value始终是一个数组
    addresses.value = Array.isArray(response) ? response : []
    console.log('addresses.value:', addresses.value)
  } catch (err) {
    console.error('获取地址列表失败:', err)
    ElMessage.error('获取地址列表失败，请稍后重试')
    // 即使出错也确保addresses.value是一个数组
    addresses.value = []
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEdit.value = false
  currentAddress.value = null
  formData.value = {
    name: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    address: '',
    is_default: false
  }
  showModal.value = true
}

const openEditModal = (address) => {
  isEdit.value = true
  currentAddress.value = address
  formData.value = {
    name: address.name,
    phone: address.phone,
    province: address.province,
    city: address.city,
    district: address.district,
    address: address.address,
    is_default: address.is_default
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    // 表单验证
    if (!formData.value.name) {
      ElMessage.error('请输入收件人姓名')
      return
    }
    if (!formData.value.phone) {
      ElMessage.error('请输入联系电话')
      return
    }
    if (!formData.value.province) {
      ElMessage.error('请输入省份')
      return
    }
    if (!formData.value.city) {
      ElMessage.error('请输入城市')
      return
    }
    if (!formData.value.district) {
      ElMessage.error('请输入区县')
      return
    }
    if (!formData.value.address) {
      ElMessage.error('请输入详细地址')
      return
    }
    
    if (isEdit.value) {
      await addressApi.updateAddress(currentAddress.value.id, formData.value)
      ElMessage.success('地址更新成功')
    } else {
      await addressApi.createAddress(formData.value)
      ElMessage.success('地址添加成功')
    }
    showModal.value = false
    fetchAddresses()
  } catch (err) {
    console.error('操作失败:', err)
    ElMessage.error(err.response?.data?.message || '操作失败，请稍后重试')
  }
}

const handleDelete = async (address) => {
  if (!confirm(`确定要删除地址"${address.name}"吗？`)) {
    return
  }
  try {
    await addressApi.deleteAddress(address.id)
    ElMessage.success('地址删除成功')
    fetchAddresses()
  } catch (err) {
    console.error('删除失败:', err)
    ElMessage.error(err.response?.data?.message || '删除失败，请稍后重试')
  }
}

const handleSetDefault = async (address) => {
  if (address.is_default) {
    return
  }
  try {
    await addressApi.setDefaultAddress(address.id)
    ElMessage.success('已设置为默认地址')
    fetchAddresses()
  } catch (err) {
    console.error('设置默认地址失败:', err)
    ElMessage.error(err.response?.data?.message || '设置默认地址失败，请稍后重试')
  }
}

onMounted(() => {
  fetchAddresses()
})
</script>

<template>
  <div class="address-book">
    <div class="page-header">
      <h3>地址管理</h3>
      <button class="btn btn-primary" @click="openCreateModal">+ 添加地址</button>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <div v-if="addresses.length === 0" class="empty">
          暂无地址，点击上方按钮添加
        </div>
        <div v-else class="address-list">
          <div v-for="address in addresses" :key="address.id" class="address-item">
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
            <div class="address-actions">
              <button v-if="!address.is_default" class="btn-sm btn-secondary" @click="handleSetDefault(address)">
                设为默认
              </button>
              <button class="btn-sm btn-secondary" @click="openEditModal(address)">
                编辑
              </button>
              <button class="btn-sm btn-danger" @click="handleDelete(address)">
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <ElDialog
      v-model="showModal"
      :title="isEdit ? '编辑地址' : '添加地址'"
      width="480px"
      center
    >
      <div class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>收件人姓名 <span class="required">*</span></label>
            <input v-model="formData.name" type="text" placeholder="请输入收件人姓名" />
          </div>
          <div class="form-group">
            <label>联系电话 <span class="required">*</span></label>
            <input v-model="formData.phone" type="text" placeholder="请输入联系电话" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>省份 <span class="required">*</span></label>
            <input v-model="formData.province" type="text" placeholder="请输入省份" />
          </div>
          <div class="form-group">
            <label>城市 <span class="required">*</span></label>
            <input v-model="formData.city" type="text" placeholder="请输入城市" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>区县 <span class="required">*</span></label>
            <input v-model="formData.district" type="text" placeholder="请输入区县" />
          </div>
        </div>
        
        <div class="form-group">
          <label>详细地址 <span class="required">*</span></label>
          <textarea v-model="formData.address" placeholder="请输入详细地址"></textarea>
        </div>
        
        <div class="form-group checkbox-group">
          <label>
            <input v-model="formData.is_default" type="checkbox" />
            <span>设为默认地址</span>
          </label>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">
            {{ isEdit ? '保存' : '添加' }}
          </button>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.address-book {
  padding: 16px;
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
  font-weight: 600;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 20px;
}

.loading, .empty {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
  font-size: 14px;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.address-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.address-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
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

.name {
  font-weight: 600;
  color: #1f2937;
  font-size: 15px;
}

.phone {
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
  margin-top: 8px;
}

.address-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 16px;
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

.btn-danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover {
  background-color: #fecaca;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 6px;
}

.modal-body {
  padding: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
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

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-group input {
  margin-right: 8px;
  width: auto;
}

.checkbox-group label {
  margin-bottom: 0;
  cursor: pointer;
}

.required {
  color: #ef4444;
  margin-left: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .address-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .address-actions {
    flex-direction: row;
    margin-left: 0;
    margin-top: 12px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
