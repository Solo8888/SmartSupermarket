<script setup>
import { ref, onMounted } from 'vue'
import * as productApi from '../../api/product'
import * as categoryApi from '../../api/category'
import { useRouter } from 'vue-router'

const router = useRouter()
const products = ref([])
const categories = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const selectedCategory = ref(null)
const searchQuery = ref('')

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
    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    const response = await productApi.getProducts(params)
    if (page.value === 1) {
      products.value = response.data.items || []
    } else {
      products.value = [...products.value, ...(response.data.items || [])]
    }
    total.value = response.data.total || 0
  } catch (err) {
    console.error('获取商品失败:', err)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await categoryApi.getAllCategories()
    categories.value = response || []
  } catch (err) {
    console.error('获取分类失败:', err)
  }
}

const handleSearch = () => {
  page.value = 1
  fetchProducts()
}

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId === selectedCategory.value ? null : categoryId
  page.value = 1
  fetchProducts()
}

const loadMore = () => {
  if (!loading.value && products.value.length < total.value) {
    page.value++
    fetchProducts()
  }
}

const formatPrice = (price) => {
  return '¥' + parseFloat(price).toFixed(2)
}

const getProductImage = (product) => {
  if (product.image_url) {
    return product.image_url
  }
  return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' + encodeURIComponent(product.name) + '&image_size=square'
}

onMounted(() => {
  fetchProducts()
  fetchCategories()
})
</script>

<template>
  <div class="customer-home">
    <div class="header">
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
    
    <div class="category-nav">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-item"
        :class="{ active: selectedCategory === category.id }"
        @click="selectCategory(category.id)"
      >
        {{ category.name }}
      </div>
    </div>
    
    <div class="product-grid">
      <div
        v-for="product in products"
        :key="product.id"
        class="product-card"
      >
        <div class="product-image">
          <img :src="getProductImage(product)" :alt="product.name" />
        </div>
        <div class="product-info">
          <div class="product-name">{{ product.name }}</div>
          <div class="product-price">{{ formatPrice(product.price) }}</div>
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

.search-bar {
  display: flex;
  gap: 8px;
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

.category-nav {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  scrollbar-width: none;
}

.category-nav::-webkit-scrollbar {
  display: none;
}

.category-item {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  white-space: nowrap;
  cursor: pointer;
  font-size: 14px;
  color: #6b7280;
  transition: all 0.2s;
}

.category-item:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.category-item.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: transparent;
  color: white;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  font-size: 16px;
  font-weight: 600;
  color: #dc2626;
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
}
</style>
