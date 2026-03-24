<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import FixedCart from '../components/FixedCart.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 购物车更新信号
const updateCart = ref(false)

const menuItems = [
  {
    name: '首页',
    path: '/customer/home',
    icon: '🏠'
  },
  {
    name: '分类',
    path: '/customer/categories',
    icon: '📁'
  },
  {
    name: '购物车',
    path: '/customer/cart',
    icon: '🛒'
  },
  {
    name: '我的',
    path: '/customer/profile',
    icon: '👤'
  }
]

const isActive = (path) => {
  return route.path === path
}

const isHomeOrCategories = computed(() => {
  return route.path === '/customer/home' || route.path === '/customer/categories'
})

const shouldHideNav = computed(() => {
  const hideNavPaths = [
    '/customer/order-detail',
    '/customer/product-detail',
    '/customer/order-review',
    '/customer/orders',
    '/customer/address-book',
    '/customer/checkout'
  ]
  
  // 检查是否是购物车页面
  if (route.path === '/customer/cart') {
    // 从商品详情页面进入购物车时隐藏导航栏
    const from = sessionStorage.getItem('fromRoute')
    const result = from === '/customer/product-detail'
    return result
  }
  
  const result = hideNavPaths.some(path => route.path.startsWith(path))
  return result
})

// 处理购物车更新
const handleCartUpdate = () => {
  updateCart.value = true
  // 重置信号
  setTimeout(() => {
    updateCart.value = false
  }, 100)
}

// 定义emit，接收子组件的更新事件
const emit = defineEmits(['update:cart'])

const handleNavClick = (path) => {
  // 当从导航栏点击购物车时，清除来源记录
  if (path === '/customer/cart') {
    sessionStorage.removeItem('fromRoute')
  }
  router.push(path)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="customer-layout">
    <main class="main-content" :class="{ 'no-nav': shouldHideNav }">
      <router-view @update:cart="handleCartUpdate" />
    </main>
    
    <!-- 只有在首页和分类页面显示购物车 -->
    <FixedCart v-if="isHomeOrCategories && !shouldHideNav" :update-cart="updateCart" />
    
    <!-- 只有在非订单和商品详情页面显示导航栏 -->
    <nav v-if="!shouldHideNav" class="bottom-nav">
      <a
        v-for="item in menuItems"
        :key="item.path"
        :href="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click.prevent="handleNavClick(item.path)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-text">{{ item.name }}</span>
      </a>
    </nav>
  </div>
</template>

<style scoped>
.customer-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 70px;
  min-height: calc(100vh - 70px);
}

/* 当隐藏导航栏时，移除底部padding */
.main-content.no-nav {
  padding-bottom: 0;
}

/* 当显示购物车时，增加底部padding */
.customer-layout:has(.fixed-cart) .main-content {
  padding-bottom: 140px;
}

/* 当隐藏导航栏时，购物车也不显示，所以不需要额外padding */
.customer-layout:has(.fixed-cart) .main-content.no-nav {
  padding-bottom: 0;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  text-decoration: none;
  color: #9ca3af;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #6b7280;
}

.nav-item.active {
  color: #3b82f6;
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
  margin-bottom: 2px;
}

.nav-text {
  font-size: 12px;
  font-weight: 500;
}

@media (min-width: 768px) {
  .customer-layout {
    max-width: 480px;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  }
  
  .bottom-nav {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>
