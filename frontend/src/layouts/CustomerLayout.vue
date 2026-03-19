<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import FixedCart from '../components/FixedCart.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

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

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="customer-layout">
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 只有在首页和分类页面显示购物车 -->
    <FixedCart v-if="isHomeOrCategories" />
    
    <nav class="bottom-nav">
      <a
        v-for="item in menuItems"
        :key="item.path"
        :href="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click.prevent="router.push(item.path)"
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
  height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 70px;
}

/* 当显示购物车时，增加底部padding */
.customer-layout:has(.fixed-cart) .main-content {
  padding-bottom: 140px;
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
