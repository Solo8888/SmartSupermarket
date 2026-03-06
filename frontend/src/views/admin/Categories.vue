<script setup>
import { ref, onMounted, computed } from 'vue'
import { categoryApi } from '../../api/category'

const categories = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const currentCategory = ref(null)
const expandedNodes = ref(new Set())

const formData = ref({
  name: '',
  parent_id: null,
  description: '',
  level: 1,
  sort_order: 0,
  status: 'active'
})

const buildTree = (flatList) => {
  const map = {}
  const roots = []
  
  flatList.forEach(item => {
    map[item.id] = { ...item, children: [] }
  })
  
  flatList.forEach(item => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id])
    } else if (!item.parent_id) {
      roots.push(map[item.id])
    }
  })
  
  return roots.sort((a, b) => a.sort_order - b.sort_order)
}

const treeCategories = computed(() => {
  return buildTree(categories.value)
})

const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await categoryApi.getCategories({ size: 1000 })
    categories.value = response.items || []
  } catch (err) {
    console.error('获取分类失败:', err)
  } finally {
    loading.value = false
  }
}

const toggleExpand = (id) => {
  if (expandedNodes.value.has(id)) {
    expandedNodes.value.delete(id)
  } else {
    expandedNodes.value.add(id)
  }
}

const openCreateModal = (parentId = null) => {
  isEdit.value = false
  currentCategory.value = null
  formData.value = {
    name: '',
    parent_id: parentId,
    description: '',
    level: parentId ? 2 : 1,
    sort_order: 0,
    status: 'active'
  }
  showModal.value = true
}

const openEditModal = (category) => {
  isEdit.value = true
  currentCategory.value = category
  formData.value = {
    name: category.name,
    parent_id: category.parent_id,
    description: category.description || '',
    level: category.level,
    sort_order: category.sort_order,
    status: category.status
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await categoryApi.updateCategory(currentCategory.value.id, formData.value)
    } else {
      await categoryApi.createCategory(formData.value)
    }
    showModal.value = false
    fetchCategories()
  } catch (err) {
    console.error('操作失败:', err)
  }
}

const handleDelete = async (category) => {
  if (!confirm(`确定要删除分类"${category.name}"吗？`)) {
    return
  }
  try {
    await categoryApi.deleteCategory(category.id)
    fetchCategories()
  } catch (err) {
    console.error('删除失败:', err)
  }
}

const renderTreeNode = (node, level = 0) => {
  const hasChildren = node.children && node.children.length > 0
  const isExpanded = expandedNodes.value.has(node.id)
  
  return `
    <div class="tree-node" style="padding-left: ${level * 24}px">
      <div class="tree-node-content">
        <span class="expand-icon" @click="toggleExpand(${node.id})" v-if="${hasChildren}">
          ${isExpanded ? '▼' : '▶'}
        </span>
        <span class="expand-placeholder" v-else></span>
        <span class="node-name">${node.name}</span>
        <span class="node-status ${node.status}">${node.status === 'active' ? '启用' : '禁用'}</span>
        <div class="node-actions">
          <button class="btn-sm btn-primary" @click="openCreateModal(${node.id})">添加子分类</button>
          <button class="btn-sm btn-secondary" @click="openEditModal(treeCategories.flatMap(n => findNode(n, ${node.id})).find(Boolean))">编辑</button>
          <button class="btn-sm btn-danger" @click="handleDelete(treeCategories.flatMap(n => findNode(n, ${node.id})).find(Boolean))">删除</button>
        </div>
      </div>
      <div v-if="${hasChildren && isExpanded}" class="tree-children">
        ${node.children.map(child => renderTreeNode(child, level + 1)).join('')}
      </div>
    </div>
  `
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div class="categories-page">
    <div class="page-header">
      <div class="header-left">
        <h3>商品分类管理</h3>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="openCreateModal()">
          + 添加根分类
        </button>
      </div>
    </div>
    
    <div class="content-card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="tree-container">
        <div v-if="treeCategories.length === 0" class="empty">
          暂无分类，点击上方按钮添加
        </div>
        <div v-else class="tree">
          <template v-for="node in treeCategories" :key="node.id">
            <div class="tree-node" :style="{ paddingLeft: '0px' }">
              <div class="tree-node-content">
                <span class="expand-icon" @click="toggleExpand(node.id)" v-if="node.children && node.children.length > 0">
                  {{ expandedNodes.has(node.id) ? '▼' : '▶' }}
                </span>
                <span class="expand-placeholder" v-else></span>
                <span class="node-name">{{ node.name }}</span>
                <span class="node-status" :class="node.status">
                  {{ node.status === 'active' ? '启用' : '禁用' }}
                </span>
                <div class="node-actions">
                  <button class="btn-sm btn-primary" @click="openCreateModal(node.id)">
                    添加子分类
                  </button>
                  <button class="btn-sm btn-secondary" @click="openEditModal(node)">
                    编辑
                  </button>
                  <button class="btn-sm btn-danger" @click="handleDelete(node)">
                    删除
                  </button>
                </div>
              </div>
              <div v-if="node.children && node.children.length > 0 && expandedNodes.has(node.id)" class="tree-children">
                <template v-for="child in node.children" :key="child.id">
                  <div class="tree-node" :style="{ paddingLeft: '24px' }">
                    <div class="tree-node-content">
                      <span class="expand-icon" @click="toggleExpand(child.id)" v-if="child.children && child.children.length > 0">
                        {{ expandedNodes.has(child.id) ? '▼' : '▶' }}
                      </span>
                      <span class="expand-placeholder" v-else></span>
                      <span class="node-name">{{ child.name }}</span>
                      <span class="node-status" :class="child.status">
                        {{ child.status === 'active' ? '启用' : '禁用' }}
                      </span>
                      <div class="node-actions">
                        <button class="btn-sm btn-primary" @click="openCreateModal(child.id)">
                          添加子分类
                        </button>
                        <button class="btn-sm btn-secondary" @click="openEditModal(child)">
                          编辑
                        </button>
                        <button class="btn-sm btn-danger" @click="handleDelete(child)">
                          删除
                        </button>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
    
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h4>{{ isEdit ? '编辑分类' : '添加分类' }}</h4>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>分类名称</label>
            <input v-model="formData.name" type="text" placeholder="请输入分类名称" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="formData.description" placeholder="请输入分类描述"></textarea>
          </div>
          <div class="form-group">
            <label>排序</label>
            <input v-model.number="formData.sort_order" type="number" placeholder="数字越小越靠前" />
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="formData.status">
              <option value="active">启用</option>
              <option value="inactive">禁用</option>
            </select>
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
.categories-page {
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

.tree-container {
  padding: 20px;
}

.tree-node {
  border-bottom: 1px solid #f3f4f6;
}

.tree-node-content {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
  transition: background-color 0.2s;
}

.tree-node-content:hover {
  background-color: #f9fafb;
}

.expand-icon {
  width: 20px;
  text-align: center;
  cursor: pointer;
  color: #6b7280;
  font-size: 12px;
  user-select: none;
}

.expand-placeholder {
  width: 20px;
}

.node-name {
  flex: 1;
  font-weight: 500;
  color: #374151;
}

.node-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.node-status.active {
  background-color: #d1fae5;
  color: #065f46;
}

.node-status.inactive {
  background-color: #fee2e2;
  color: #991b1b;
}

.node-actions {
  display: flex;
  gap: 8px;
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

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 6px;
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
  
  .tree-node-content {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .node-actions {
    width: 100%;
    justify-content: flex-start;
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
