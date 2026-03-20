<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as categoryApi from '../../api/category'
import * as productApi from '../../api/product'
import * as cartApi from '../../api/cart'

const categories = ref([])
const products = ref([])
const loading = ref(false)
const selectedCategory = ref(null)
const selectedLevel1Category = ref(null)
const selectedLevel2Category = ref(null)

// 计算一级分类
const level1Categories = computed(() => {
  return categories.value.filter(cat => !cat.parent_id || cat.parent_id === '')
})

// 计算二级分类
const level2Categories = computed(() => {
  if (!selectedLevel1Category.value) return []
  return categories.value.filter(cat => cat.parent_id === selectedLevel1Category.value.id)
})

// 计算三级分类
const level3Categories = computed(() => {
  if (!selectedLevel2Category.value) return []
  return categories.value.filter(cat => cat.parent_id === selectedLevel2Category.value.id)
})

const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await categoryApi.getAllCategories()
    categories.value = response || []
    // 默认选中第一个一级分类
    if (level1Categories.value.length > 0) {
      selectLevel1Category(level1Categories.value[0])
      // 选中一级分类后，默认选中第一个二级分类（如果有的话）
      // 这里使用 setTimeout 确保 level2Categories 计算属性已经更新
      setTimeout(() => {
        if (level2Categories.value.length > 0) {
          selectLevel2Category(level2Categories.value[0])
        }
      }, 0)
    }
  } catch (err) {
    console.error('获取分类失败:', err)
    ElMessage.error('获取分类失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const fetchProductsByCategory = async (categoryId) => {
  loading.value = true
  try {
    const response = await productApi.getProductsByCategory(categoryId)
    products.value = response || []
  } catch (err) {
    console.error('获取商品失败:', err)
    ElMessage.error('获取商品失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const selectLevel1Category = (category) => {
  selectedLevel1Category.value = category
  selectedLevel2Category.value = null
  selectedCategory.value = category
  fetchProductsByCategory(category.id)
}

const selectLevel2Category = (category) => {
  selectedLevel2Category.value = category
  // 如果有三级分类，默认选中第一个三级分类
  if (level3Categories.value.length > 0) {
    const firstLevel3Category = level3Categories.value[0]
    selectLevel3Category(firstLevel3Category)
  } else {
    // 如果没有三级分类，直接加载二级分类的商品
    selectedCategory.value = category
    fetchProductsByCategory(category.id)
  }
}

const selectLevel3Category = (category) => {
  selectedCategory.value = category
  fetchProductsByCategory(category.id)
}

const addToCart = async (product) => {
  try {
    await cartApi.addToCart({
      product_id: product.id,
      quantity: 1
    })
    ElMessage.success('已添加到购物车')
  } catch (err) {
    console.error('添加到购物车失败:', err)
    ElMessage.error('添加到购物车失败，请稍后重试')
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div class="categories-page">
    <div class="page-header">
      <h3>商品分类</h3>
    </div>
    
    <!-- 上半部分：一级分类（水平滚动） -->
    <div class="category-nav">
      <div 
        v-for="category in level1Categories" 
        :key="category.id"
        class="category-item"
        :class="{ active: selectedLevel1Category?.id === category.id }"
        @click="selectLevel1Category(category)"
      >
        {{ category.name }}
      </div>
    </div>
    
    <!-- 下半部分：二级分类和商品列表 -->
    <div class="content">
      <!-- 左侧：二级分类 -->
      <div class="level2-categories">
        <div 
          v-for="category in level2Categories" 
          :key="category.id"
          class="level2-item"
          :class="{ active: selectedLevel2Category?.id === category.id }"
          @click="selectLevel2Category(category)"
        >
          {{ category.name }}
        </div>
        <div v-if="level2Categories.length === 0 && selectedLevel1Category" class="empty-category">
          暂无二级分类
        </div>
      </div>
      
      <!-- 右侧：三级分类和商品列表 -->
      <div class="products-wrapper">
        <!-- 三级分类 -->
        <div v-if="level3Categories.length > 0" class="level3-categories">
          <div 
            v-for="category in level3Categories" 
            :key="category.id"
            class="level3-item"
            :class="{ active: selectedCategory?.id === category.id }"
            @click="selectLevel3Category(category)"
          >
            {{ category.name }}
          </div>
        </div>
        
        <!-- 商品列表 -->
        <div class="products-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="!selectedCategory" class="empty">
            请选择分类查看商品
          </div>
          <div v-else-if="products.length === 0" class="empty">
            该分类暂无商品
          </div>
          <div v-else class="products-list-view">
          <div v-for="product in products" :key="product.id" class="product-item">
            <div class="product-image">
              <img :src="product.image_url" :alt="product.name" />
            </div>
            <div class="product-info">
              <h4 class="product-name">{{ product.name }}</h4>
              <p class="product-price">¥{{ product.price.toFixed(2) }}</p>
            </div>
            <div class="product-actions">
              <button class="add-to-cart-btn" @click="addToCart(product)">
                🛒
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.categories-page {
  padding: 16px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
}

.category-nav {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 12px 0;
  margin-bottom: 16px;
  scrollbar-width: none;
}

.category-nav::-webkit-scrollbar {
  display: none;
}

.category-item {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  white-space: nowrap;
  cursor: pointer;
  font-size: 14px;
  color: #6b7280;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.category-item:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-2px);
}

.category-item.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: transparent;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.content {
  display: flex;
  gap: 16px;
  min-height: 400px;
  max-height: calc(100vh - 240px);
}

/* 二级分类样式 */
.level2-categories {
  width: 120px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
}

.level2-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  color: #6b7280;
}

.level2-item:hover {
  background-color: #f9fafb;
  color: #3b82f6;
}

.level2-item.active {
  background-color: #e0f2fe;
  color: #0284c7;
  font-weight: 600;
  border-left: 3px solid #3b82f6;
}

.empty-category {
  padding: 20px 12px;
  text-align: center;
  color: #9ca3af;
  font-size: 12px;
}

.products-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* 三级分类样式 */
.level3-categories {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  scrollbar-width: none;
}

.level3-categories::-webkit-scrollbar {
  display: none;
}

.level3-item {
  padding: 6px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  white-space: nowrap;
  cursor: pointer;
  font-size: 13px;
  color: #6b7280;
  transition: all 0.2s;
}

.level3-item:hover {
  border-color: #93c5fd;
  color: #3b82f6;
}

.level3-item.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: transparent;
  color: white;
  font-weight: 500;
}

.products-list {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.loading, .empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #9ca3af;
  font-size: 14px;
}

.products-list-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  transition: all 0.2s;
}

.product-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: white;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 500;
  color: #1f2937;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #ef4444;
}

.product-actions {
  flex-shrink: 0;
}

.add-to-cart-btn {
  width: 30px;
  height: 30px;
  border: 2px solid #3b82f6;
  border-radius: 50%;
  background: white;
  color: #3b82f6;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-to-cart-btn:hover {
  background: #3b82f6;
  color: white;
  transform: scale(1.1);
}

.add-to-cart-btn:active {
  transform: scale(0.95);
}

@media (max-width: 480px) {
  .content {
    height: calc(100vh - 160px);
  }
  
  .categories-list {
    width: 100px;
  }
  
  .category-item {
    padding: 12px;
    font-size: 13px;
  }
  
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .product-image {
    height: 100px;
  }
  
  .product-info {
    padding: 10px;
  }
  
  .product-name {
    font-size: 13px;
  }
  
  .product-price {
    font-size: 14px;
  }
}
</style>