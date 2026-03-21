<script setup>
import { ref, onMounted } from 'vue'
import * as productApi from '../../api/product'
import * as categoryApi from '../../api/category'
import * as uploadApi from '../../api/upload'
import CategoryCascader from '../../components/CategoryCascader.vue'
import { ElDialog } from 'element-plus'

const products = ref([])
const categories = ref([])
const loading = ref(false)
const uploading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const currentProduct = ref(null)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const imagePreview = ref('')
const imageFile = ref(null)
const searchQuery = ref('')

const formData = ref({
  name: '',
  category_id: null,
  price: 0,
  purchase_price: 0,
  original_price: null,
  description: '',
  image_url: '',
  barcode: '',
  brand: '',
  origin: '',
  shelf_life: null,
  unit: '个',
  status: 'active'
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await productApi.getProducts(params)
    products.value = response.items || []
    total.value = response.total || 0
  } catch (err) {
    console.error('获取商品失败:', err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchProducts()
}

const clearSearch = () => {
  searchQuery.value = ''
  page.value = 1
  fetchProducts()
}

const fetchCategories = async () => {
  try {
    const response = await categoryApi.getAllCategories()
    categories.value = response || []
  } catch (err) {
    console.error('获取分类失败:', err)
  }
}

const openCreateModal = () => {
  isEdit.value = false
  currentProduct.value = null
  imagePreview.value = ''
  imageFile.value = null
  formData.value = {
    name: '',
    category_id: null,
    price: 0,
    purchase_price: 0,
    original_price: null,
    description: '',
    image_url: '',
    barcode: '',
    brand: '',
    origin: '',
    shelf_life: null,
    unit: '个',
    status: 'active'
  }
  showModal.value = true
}

const openEditModal = (product) => {
  isEdit.value = true
  currentProduct.value = product
  imagePreview.value = product.image_url || ''
  imageFile.value = null
  formData.value = {
    name: product.name,
    category_id: product.category_id,
    price: product.price,
    purchase_price: product.purchase_price || 0,
    original_price: product.original_price || null,
    description: product.description || '',
    image_url: product.image_url || '',
    barcode: product.barcode || '',
    brand: product.brand || '',
    origin: product.origin || '',
    shelf_life: product.shelf_life || null,
    unit: product.unit || '个',
    status: product.status
  }
  showModal.value = true
}

const handleImageChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleImageUpload = async () => {
  if (!imageFile.value) {
    return
  }
  uploading.value = true
  try {
    const response = await uploadApi.uploadImage(imageFile.value)
    formData.value.image_url = response.url
    imagePreview.value = response.url
  } catch (err) {
    console.error('上传图片失败:', err)
  } finally {
    uploading.value = false
  }
}

const clearImage = () => {
  imagePreview.value = ''
  imageFile.value = null
  formData.value.image_url = ''
}

const handleSubmit = async () => {
  try {
    // 表单验证
    if (!formData.value.name) {
      alert('请输入商品名称')
      return
    }
    if (!formData.value.category_id) {
      alert('请选择商品分类')
      return
    }
    if (!formData.value.barcode || !formData.value.barcode.trim()) {
      alert('请输入商品条码')
      return
    }
    if (formData.value.price <= 0) {
      alert('请输入有效的售价')
      return
    }
    if (formData.value.purchase_price <= 0) {
      alert('请输入有效的进货价格')
      return
    }
    
    if (imageFile.value && !formData.value.image_url) {
      await handleImageUpload()
    }
    
    if (isEdit.value) {
      await productApi.updateProduct(currentProduct.value.id, formData.value)
    } else {
      await productApi.createProduct(formData.value)
    }
    showModal.value = false
    fetchProducts()
  } catch (err) {
    console.error('操作失败:', err)
  }
}

const handleDelete = async (product) => {
  if (!confirm(`确定要删除商品"${product.name}"吗？`)) {
    return
  }
  try {
    await productApi.deleteProduct(product.id)
    fetchProducts()
  } catch (err) {
    console.error('删除失败:', err)
  }
}

const getStatusText = (status) => {
  const statusMap = {
    'active': '启用',
    'inactive': '禁用',
    'out_of_stock': '缺货'
  }
  return statusMap[status] || status
}

const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : '未分类'
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchProducts()
}

onMounted(() => {
  fetchProducts()
  fetchCategories()
})
</script>

<template>
  <div class="products-page">
    <div class="page-header">
      <div class="header-left">
        <h3>商品管理</h3>
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
        <button class="btn btn-primary" @click="openCreateModal()">
          + 添加商品
        </button>
      </div>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else>
        <div v-if="products.length === 0" class="empty">
          暂无商品，点击上方按钮添加
        </div>
        <div v-else>
          <div class="table-wrapper">
            <table class="product-table">
              <thead>
                <tr>
                  <th>图片</th>
                  <th>商品名称</th>
                  <th>分类</th>
                  <th>条码</th>
                  <th>品牌</th>
                  <th>单位</th>
                  <th>售价</th>
                  <th>原价</th>
                  <th>销量</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in products" :key="product.id">
                  <td>
                    <div v-if="product.image_url" class="product-image">
                      <img :src="product.image_url.startsWith('http') ? product.image_url : window.location.origin + product.image_url" :alt="product.name" />
                    </div>
                    <span v-else class="no-image">-</span>
                  </td>
                  <td class="product-name">{{ product.name }}</td>
                  <td>{{ getCategoryName(product.category_id) }}</td>
                  <td>{{ product.barcode || '-' }}</td>
                  <td>{{ product.brand || '-' }}</td>
                  <td>{{ product.unit || '-' }}</td>
                  <td>¥{{ product.price }}</td>
                  <td>{{ product.original_price ? '¥' + product.original_price : '-' }}</td>
                  <td>{{ product.sales_count || 0 }}</td>
                  <td>
                    <span class="status-badge" :class="product.status">
                      {{ getStatusText(product.status) }}
                    </span>
                  </td>
                  <td>
                    <div class="actions">
                      <button class="btn-sm btn-secondary" @click="openEditModal(product)">
                        编辑
                      </button>
                      <button class="btn-sm btn-danger" @click="handleDelete(product)">
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
    
    <ElDialog
      v-model="showModal"
      :title="isEdit ? '编辑商品' : '添加商品'"
      width="640px"
      center
    >
      <div class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>商品名称 <span class="required">*</span></label>
            <input v-model="formData.name" type="text" placeholder="请输入商品名称" />
          </div>
          <div class="form-group">
            <label>条码 <span class="required">*</span></label>
            <input v-model="formData.barcode" type="text" placeholder="请输入商品条码" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>分类 <span class="required">*</span></label>
            <CategoryCascader 
              v-model="formData.category_id" 
              :categories="categories"
              placeholder="请选择分类"
            />
          </div>
          <div class="form-group">
            <label>品牌</label>
            <input v-model="formData.brand" type="text" placeholder="请输入品牌" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>售价 <span class="required">*</span></label>
            <input v-model.number="formData.price" type="number" step="0.01" placeholder="请输入售价" />
          </div>
          <div class="form-group">
            <label>进货价格 <span class="required">*</span></label>
            <input v-model.number="formData.purchase_price" type="number" step="0.01" placeholder="请输入进货价格" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>原价</label>
            <input v-model.number="formData.original_price" type="number" step="0.01" placeholder="请输入原价" />
          </div>
          <div class="form-group">
            <label>产地</label>
            <input v-model="formData.origin" type="text" placeholder="请输入产地" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>保质期（天）</label>
            <input v-model.number="formData.shelf_life" type="number" min="0" placeholder="请输入保质期" />
          </div>
          <div class="form-group">
            <label>品牌</label>
            <input v-model="formData.brand" type="text" placeholder="请输入品牌" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>单位</label>
            <input v-model="formData.unit" type="text" placeholder="请输入单位" />
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="formData.status">
              <option value="active">启用</option>
              <option value="inactive">禁用</option>
              <option value="out_of_stock">缺货</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label>商品图片</label>
          <div class="image-upload-area">
            <div v-if="imagePreview" class="image-preview">
              <img :src="imagePreview" alt="预览" />
              <button type="button" class="clear-image-btn" @click="clearImage">×</button>
            </div>
            <div v-else class="image-placeholder">
              <input 
                type="file" 
                accept="image/*" 
                @change="handleImageChange"
                ref="fileInput"
                style="display: none"
              />
              <button type="button" class="btn btn-secondary" @click="$refs.fileInput.click()">
                选择图片
              </button>
            </div>
            <div v-if="imageFile && !formData.image_url" class="upload-status">
              <span v-if="uploading" class="uploading-text">上传中...</span>
              <span v-else class="upload-hint">已选择图片，点击创建/保存时自动上传</span>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="formData.description" placeholder="请输入商品描述"></textarea>
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
.products-page {
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

.product-table {
  width: 100%;
  border-collapse: collapse;
}

.product-table th,
.product-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.product-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.product-table td {
  color: #4b5563;
  font-size: 14px;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #9ca3af;
}

.product-name {
  font-weight: 500;
  color: #1f2937;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-badge.out_of_stock {
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

.btn-danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover {
  background-color: #fecaca;
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

.image-upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 200px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.clear-image-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-image-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 200px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
}

.upload-status {
  margin-top: 8px;
  font-size: 14px;
}

.uploading-text {
  color: #3b82f6;
  font-weight: 500;
}

.upload-hint {
  color: #6b7280;
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
  
  .table-wrapper {
    padding: 12px;
  }
  
  .product-table th,
  .product-table td {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .product-image {
    width: 50px;
    height: 50px;
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
