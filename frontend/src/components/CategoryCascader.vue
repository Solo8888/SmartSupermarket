<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Number,
    default: null
  },
  placeholder: {
    type: String,
    default: '请选择分类'
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedPath = ref([])
const isOpen = ref(false)

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
  
  const sortChildren = (nodes) => {
    nodes.sort((a, b) => a.sort_order - b.sort_order)
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        sortChildren(node.children)
      }
    })
  }
  
  sortChildren(roots)
  return roots
}

const treeCategories = computed(() => {
  return buildTree(props.categories)
})

const findPathById = (id, nodes, path = []) => {
  for (const node of nodes) {
    const newPath = [...path, node]
    if (node.id === id) {
      return newPath
    }
    if (node.children && node.children.length > 0) {
      const result = findPathById(id, node.children, newPath)
      if (result) {
        return result
      }
    }
  }
  return null
}

const getSelectedText = () => {
  if (selectedPath.value.length === 0) {
    return props.placeholder
  }
  return selectedPath.value.map(n => n.name).join(' / ')
}

const selectCategory = (category, level) => {
  selectedPath.value = selectedPath.value.slice(0, level)
  selectedPath.value.push(category)
  
  if (!category.children || category.children.length === 0) {
    emit('update:modelValue', category.id)
    isOpen.value = false
  }
}

const clearSelection = () => {
  selectedPath.value = []
  emit('update:modelValue', null)
}

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    const path = findPathById(newVal, treeCategories.value)
    selectedPath.value = path || []
  } else {
    selectedPath.value = []
  }
}, { immediate: true })
</script>

<template>
  <div class="category-cascader">
    <div class="cascader-trigger" @click="toggleDropdown">
      <span class="selected-text" :class="{ placeholder: selectedPath.length === 0 }">
        {{ getSelectedText() }}
      </span>
      <span v-if="selectedPath.length > 0" class="clear-btn" @click.stop="clearSelection">×</span>
      <span class="arrow">{{ isOpen ? '▲' : '▼' }}</span>
    </div>
    
    <div v-if="isOpen" class="cascader-dropdown">
      <div class="cascader-panels">
        <div v-for="(level, index) in selectedPath.length + 1" :key="index" class="cascader-panel">
          <div 
            v-for="category in (index === 0 ? treeCategories : selectedPath[index - 1]?.children || [])"
            :key="category.id"
            class="cascader-option"
            :class="{ active: selectedPath[index]?.id === category.id }"
            @click="selectCategory(category, index)"
          >
            {{ category.name }}
            <span v-if="category.children && category.children.length > 0" class="option-arrow">▶</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-cascader {
  position: relative;
  width: 100%;
}

.cascader-trigger {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.cascader-trigger:hover {
  border-color: #9ca3af;
}

.selected-text {
  flex: 1;
  color: #1f2937;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-text.placeholder {
  color: #9ca3af;
}

.clear-btn {
  margin-right: 8px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #d1d5db;
  color: #374151;
}

.arrow {
  color: #9ca3af;
  font-size: 10px;
}

.cascader-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 1000;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.cascader-panels {
  display: flex;
  max-height: 300px;
}

.cascader-panel {
  min-width: 160px;
  max-width: 200px;
  border-right: 1px solid #f3f4f6;
  overflow-y: auto;
}

.cascader-panel:last-child {
  border-right: none;
}

.cascader-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #374151;
}

.cascader-option:hover {
  background: #f3f4f6;
}

.cascader-option.active {
  background: #eff6ff;
  color: #1d4ed8;
}

.option-arrow {
  color: #9ca3af;
  font-size: 12px;
}
</style>
