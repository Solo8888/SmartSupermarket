<script setup>
import { defineOptions } from 'vue'

defineOptions({
  name: 'TreeNode'
})

const props = defineProps({
  node: { type: Object, required: true },
  level: { type: Number, required: true },
  parentId: { type: Number, default: null },
  expandedNodes: { type: Map, required: true },
  isExpanded: { type: Function, required: true },
  toggleExpand: { type: Function, required: true },
  openCreateModal: { type: Function, required: true },
  openEditModal: { type: Function, required: true },
  handleDelete: { type: Function, required: true }
})
</script>

<template>
  <div class="tree-node" :style="{ paddingLeft: level * 24 + 'px' }">
    <div class="tree-node-content">
      <span 
        class="expand-icon" 
        @click="toggleExpand(node, parentId)" 
        v-if="node.children && node.children.length > 0"
      >
        {{ isExpanded(node, parentId) ? '▼' : '▶' }}
      </span>
      <span class="expand-placeholder" v-else></span>
      <span class="node-name">{{ node.name }}</span>
      <span class="node-status" :class="node.status">
        {{ node.status === 'active' ? '启用' : '禁用' }}
      </span>
      <div class="node-actions">
        <button class="btn-sm btn-primary" @click="openCreateModal(node.id, node.level)">
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
    <div v-if="node.children && node.children.length > 0 && isExpanded(node, parentId)" class="tree-children">
      <TreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        :parent-id="node.id"
        :expanded-nodes="expandedNodes"
        :is-expanded="isExpanded"
        :toggle-expand="toggleExpand"
        :open-create-modal="openCreateModal"
        :open-edit-modal="openEditModal"
        :handle-delete="handleDelete"
      />
    </div>
  </div>
</template>

<style scoped>
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

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
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

@media (max-width: 768px) {
  .tree-node-content {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .node-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
