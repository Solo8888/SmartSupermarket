<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as categoryApi from '../../api/category'
import * as productApi from '../../api/product'
import * as cartApi from '../../api/cart'
import * as storeApi from '../../api/store'
import { useStoreStore } from '../../stores/store'

const storeStore = useStoreStore()
const router = useRouter()
const categories = ref([])
const products = ref([])
const cartItems = ref([])
const loading = ref(false)
const selectedCategory = ref(null)
const selectedLevel1Category = ref(null)
const selectedLevel2Category = ref(null)
const showStoreDropdown = ref(false)

// 从store中获取选中的门店和门店列表
const selectedStore = computed(() => storeStore.selectedStore)
const stores = computed(() => storeStore.stores)

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

// 获取购物车中商品的数量
const getProductQuantity = (productId) => {
  const item = cartItems.value.find(item => item.product_id === productId)
  return item ? item.quantity : 0
}

// 商品是否在购物车中
const isInCart = (productId) => {
  return getProductQuantity(productId) > 0
}

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

const fetchStores = async () => {
  try {
    const response = await storeApi.getAllStores()
    storeStore.setStores(response || [])
    // 默认选择第一个门店
    if (stores.value.length > 0 && !selectedStore.value) {
      storeStore.setSelectedStore(stores.value[0])
    }
  } catch (err) {
    console.error('获取门店列表失败:', err)
  }
}

const fetchProductsByCategory = async (categoryId) => {
  loading.value = true
  try {
    const params = {}
    if (selectedStore.value) {
      params.store_id = selectedStore.value.id
    }
    const response = await productApi.getProductsByCategory(categoryId, params)
        products.value = response || []
        // 按库存数量从多到少排序，让有库存的商品优先展示
        products.value = products.value.sort((a, b) => {
          const stockA = a.stock || 0
          const stockB = b.stock || 0
          return stockB - stockA
        })
  } catch (err) {
    console.error('获取商品失败:', err)
    ElMessage.error('获取商品失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const fetchCart = async () => {
  try {
    const response = await cartApi.getCartItems()
    cartItems.value = response.items || []
  } catch (err) {
    console.error('获取购物车失败:', err)
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
    // 更新购物车数据
    await fetchCart()
    // 通知父组件更新购物车
    emit('update:cart')
  } catch (err) {
    console.error('添加到购物车失败:', err)
    ElMessage.error('添加到购物车失败，请稍后重试')
  }
}

const toggleStoreDropdown = () => {
  showStoreDropdown.value = !showStoreDropdown.value
}

const selectStore = (store) => {
  storeStore.setSelectedStore(store)
  showStoreDropdown.value = false
  // 如果已经选择了分类，重新获取商品
  if (selectedCategory.value) {
    fetchProductsByCategory(selectedCategory.value.id)
  }
}

// 定义emit
const emit = defineEmits(['update:cart'])

onMounted(async () => {
  await fetchStores()
  fetchCategories()
  fetchCart()
})
</script>

<template>
  <div class="categories-page">
    <div class="page-header">
      <h3>商品分类</h3>
      <!-- 门店选择区域 -->
      <div class="store-selector">
        <div class="store-dropdown" @click="toggleStoreDropdown">
          <span class="store-name">{{ selectedStore?.name || '选择门店' }}</span>
          <span class="dropdown-arrow">{{ showStoreDropdown ? '▼' : '▶' }}</span>
        </div>
        <div v-if="showStoreDropdown" class="store-dropdown-menu">
          <div 
            v-for="store in stores" 
            :key="store.id"
            class="store-item"
            :class="{ active: selectedStore?.id === store.id }"
            @click="selectStore(store)"
          >
            {{ store.name }}
          </div>
        </div>
      </div>
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
          <div v-for="product in products" :key="product.id" class="product-item" @click="router.push(`/customer/product-detail/${product.id}`)" style="cursor: pointer">
            <div class="product-image" :class="{ 'out-of-stock': (product.stock || 0) <= 0 }">
              <img :src="product.image_url && product.image_url.startsWith('http') ? product.image_url : (product.image_url ? window.location.origin + product.image_url : 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' + encodeURIComponent(product.name || '商品') + '&image_size=square')" :alt="product.name" />
            </div>
            <div class="product-info">
              <h4 class="product-name">{{ product.name }}</h4>
              <p class="product-price">¥{{ parseFloat(product.price).toFixed(2) }}</p>
            </div>
            <div class="product-actions">
              <button class="add-to-cart-btn" @click.stop="addToCart(product)" :class="{ 'in-cart': isInCart(product.id), 'out-of-stock': (product.stock || 0) <= 0 }" :disabled="(product.stock || 0) <= 0">
                🛒
                <span v-if="isInCart(product.id)" class="cart-badge">{{ getProductQuantity(product.id) }}</span>
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
  padding: 0;
}

.page-header {
  padding: 16px;
  margin-bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
}

/* 门店选择器样式 */
.store-selector {
  position: relative;
}

.store-dropdown {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  min-width: 120px;
}

.store-dropdown:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.store-name {
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 11px;
  color: #6b7280;
  transition: transform 0.2s;
  margin-left: 6px;
}

.store-dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-top: 4px;
  max-height: 180px;
  overflow-y: auto;
  z-index: 1000;
  min-width: 180px;
}

.store-item {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: all 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.store-item:last-child {
  border-bottom: none;
  border-radius: 0 0 12px 12px;
}

.store-item:hover {
  background-color: #f3f4f6;
  color: #3b82f6;
}

.store-item.active {
  background-color: #e0f2fe;
  color: #0284c7;
  font-weight: 600;
}

.category-nav {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 12px 16px;
  margin-bottom: 0;
  scrollbar-width: none;
  background: white;
  border-bottom: 1px solid #f3f4f6;
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
  gap: 0;
  min-height: 400px;
  max-height: calc(100vh - 200px);
  background: white;
}

/* 二级分类样式 */
.level2-categories {
  width: 30%;
  max-width: 100px;
  background: #f9fafb;
  border-right: 1px solid #f3f4f6;
  overflow-y: auto;
  padding: 0;
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
  background-color: #f3f4f6;
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
  flex-basis: 70%;
  display: flex;
  flex-direction: column;
  background: white;
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
  background: white;
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
  position: relative;
}

.product-image.out-of-stock::after {
  content: '补货中';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: relative;
  z-index: 0;
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
  position: relative;
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
  position: relative;
}

.add-to-cart-btn:hover {
  background: #3b82f6;
  color: white;
  transform: scale(1.1);
}

.add-to-cart-btn:active {
  transform: scale(0.95);
}

.add-to-cart-btn.in-cart {
  background: #3b82f6;
  color: white;
}

.add-to-cart-btn.out-of-stock {
  border-color: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
  background: #f3f4f6;
}

.add-to-cart-btn.out-of-stock:hover {
  background: #f3f4f6;
  color: #9ca3af;
  transform: none;
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

@media (max-width: 480px) {
  .content {
    height: calc(100vh - 160px);
  }
  
  .level2-categories {
    width: 90px;
  }
  
  .category-item {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .product-image {
    width: 60px;
    height: 60px;
  }
  
  .product-name {
    font-size: 13px;
  }
  
  .product-price {
    font-size: 14px;
  }
  
  .add-to-cart-btn {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
}
</style>