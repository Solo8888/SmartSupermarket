<script setup>
import { ref, onMounted, computed } from 'vue'
import * as productApi from '../../api/product'
import * as storeApi from '../../api/store'
import recommendationApi from '../../api/recommendation'
import { useRouter } from 'vue-router'
import { useStoreStore } from '../../stores/store'

const router = useRouter()
const storeStore = useStoreStore()
const products = ref([])
const recommendedProducts = ref([])
const loading = ref(false)
const recommendLoading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const searchQuery = ref('')
const showStoreDropdown = ref(false)

// 从store中获取选中的门店和门店列表
const selectedStore = computed(() => storeStore.selectedStore)
const stores = computed(() => storeStore.stores)

const fetchStores = async () => {
  try {
    const response = await storeApi.getAllStores()
    storeStore.setStores(response || [])
    // 如果没有选中的门店，默认选择第一个
    if (stores.value.length > 0 && !selectedStore.value) {
      storeStore.setSelectedStore(stores.value[0])
    }
  } catch (err) {
    console.error('获取门店列表失败:', err)
  }
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { 
      page: page.value, 
      size: size.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (selectedStore.value) {
      params.store_id = selectedStore.value.id
    }
    const response = await productApi.getProducts(params)
    let newProducts = response.items || []
        // 过滤掉库存为0的商品
        newProducts = newProducts.filter(product => {
          // 假设商品对象中有 stock 或 inventory 字段表示库存
          const stock = product.stock || product.inventory || product.quantity || 0
          return stock > 0
        })
        // 按库存数量从多到少排序，让有库存的商品优先展示
        if (page.value === 1) {
          newProducts = newProducts.sort((a, b) => {
            const stockA = a.stock || a.inventory || a.quantity || 0
            const stockB = b.stock || b.inventory || b.quantity || 0
            return stockB - stockA
          })
        }
    if (page.value === 1) {
      products.value = newProducts
    } else {
      products.value = [...products.value, ...newProducts]
    }
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

const loadMore = () => {
  if (!loading.value && products.value.length < total.value) {
    page.value++
    fetchProducts()
  }
}

const toggleStoreDropdown = () => {
  showStoreDropdown.value = !showStoreDropdown.value
}

const selectStore = (store) => {
  storeStore.setSelectedStore(store)
  showStoreDropdown.value = false
  page.value = 1
  fetchProducts()
  fetchRecommendedProducts()
}

const fetchRecommendedProducts = async () => {
  recommendLoading.value = true
  try {
    const params = {
      limit: 10
    }
    if (selectedStore.value) {
      params.store_id = selectedStore.value.id
    }
    const response = await recommendationApi.getPersonalizedRecommendations(params)
    recommendedProducts.value = response.products || []
  } catch (err) {
    console.error('获取推荐商品失败:', err)
  } finally {
    recommendLoading.value = false
  }
}

const formatPrice = (price) => {
  return '¥' + parseFloat(price).toFixed(2)
}

const getProductImage = (product) => {
  if (product.image_url) {
    if (product.image_url.startsWith('http')) {
      return product.image_url
    }
    return window.location.origin + product.image_url
  }
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' + encodeURIComponent(product.name || '商品') + '&image_size=square'
}

onMounted(async () => {
  await fetchStores()
  fetchProducts()
  fetchRecommendedProducts()
})
</script>

<template>
  <div class="customer-home">
    <div class="header">
      <div class="header-content">
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
        
        <!-- 搜索栏 -->
        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索商品..."
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch">🔍</button>
        </div>
      </div>
    </div>
    
    <!-- 推荐商品区域 -->
    <div class="recommendations-section">
      <div class="section-header">
        <h3>为您推荐</h3>
        <span class="section-subtitle">根据您的喜好精选</span>
      </div>
      
      <div v-if="recommendLoading" class="loading">加载中...</div>
      <div v-else-if="recommendedProducts.length === 0" class="empty">暂无推荐商品</div>
      <div v-else class="recommendation-grid">
        <div
          v-for="(product, index) in recommendedProducts"
          :key="product.id || index"
          class="recommendation-card"
          @click="router.push(`/customer/product-detail/${product.id}`)"
          style="cursor: pointer"
        >
          <div class="recommendation-image">
            <img :src="getProductImage(product)" :alt="product.name || '商品'" />
          </div>
          <div class="recommendation-info">
            <div class="recommendation-name">{{ product.name || '未知商品' }}</div>
            <div class="recommendation-price">{{ formatPrice(product.price || 0) }}</div>
            <div class="recommendation-reason">{{ product.reason || '推荐商品' }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 全部商品区域 -->
    <div class="section-header">
      <h3>全部商品</h3>
    </div>
    
    <div class="product-grid">
      <div
        v-for="(product, index) in products"
        :key="product.id || index"
        class="product-card"
        @click="router.push(`/customer/product-detail/${product.id}`)"
        style="cursor: pointer"
      >
        <div class="product-image">
          <img :src="getProductImage(product)" :alt="product.name || '商品'" />
        </div>
        <div class="product-info">
          <div class="product-name">{{ product.name || '未知商品' }}</div>
          <div class="product-price">{{ formatPrice(product.price || 0) }}</div>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="products.length === 0" class="empty">暂无商品</div>
    <div v-else-if="products.length < total" class="load-more" @click="loadMore">
      加载更多
    </div>
  </div>
</template>

<style scoped>
.customer-home {
  padding: 16px;
}

.header {
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* 区域标题样式 */
.section-header {
  margin: 24px 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.section-subtitle {
  font-size: 14px;
  color: #6b7280;
}

/* 推荐商品区域样式 */
.recommendations-section {
  margin: 20px 0;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.recommendation-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.recommendation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-image {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #f9fafb;
}

.recommendation-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.recommendation-card:hover .recommendation-image img {
  transform: scale(1.05);
}

.recommendation-info {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.recommendation-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  line-height: 1.4;
  flex: 1;
}

.recommendation-price {
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
  margin: 4px 0;
}

.recommendation-reason {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 12px;
  align-self: flex-start;
}

/* 门店选择器样式 */
.store-selector {
  position: relative;
  flex-shrink: 0;
}

.store-dropdown {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.store-dropdown:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.store-name {
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 12px;
  color: #6b7280;
  transition: transform 0.2s;
}

.store-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.store-item {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 14px;
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

/* 搜索栏样式 */
.search-bar {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
}

.search-bar input:focus {
  border-color: #3b82f6;
}

.search-bar button {
  padding: 12px 20px;
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  font-size: 16px;
  cursor: pointer;
}



.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-image {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #f9fafb;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
  line-height: 1.4;
}

.product-price {
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
  margin-top: auto;
}

.loading,
.empty,
.load-more {
  text-align: center;
  padding: 24px;
  color: #9ca3af;
  font-size: 14px;
}

.load-more {
  cursor: pointer;
  color: #3b82f6;
}

.load-more:hover {
  color: #1d4ed8;
}

@media (min-width: 480px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .recommendation-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .recommendation-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
