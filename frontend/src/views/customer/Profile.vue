<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar">
        <span class="avatar-text">{{ userAvatar }}</span>
      </div>
      <div class="user-info">
        <div class="username">{{ userStore.user?.name || '顾客' }}</div>
        <div class="phone">{{ userStore.user?.phone || '' }}</div>
      </div>
    </div>
    
    <div class="menu-list">
      <div class="menu-section">
        <div class="menu-item" @click="goToOrders">
          <span class="menu-icon">📋</span>
          <span class="menu-text">我的订单</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="goToAddress">
          <span class="menu-icon">📍</span>
          <span class="menu-text">收货地址</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
      
      <div class="menu-section">
        <div class="menu-item" @click="goToSettings">
          <span class="menu-icon">⚙️</span>
          <span class="menu-text">设置</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="goToAbout">
          <span class="menu-icon">ℹ️</span>
          <span class="menu-text">关于我们</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
      
      <div class="menu-section">
        <div class="menu-item logout" @click="logout">
          <span class="menu-icon">🚪</span>
          <span class="menu-text">退出登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const userAvatar = computed(() => {
  const name = userStore.user?.name || '顾客'
  return name.charAt(0).toUpperCase()
})

const goToOrders = () => {
  alert('我的订单功能开发中...')
}

const goToAddress = () => {
  alert('收货地址功能开发中...')
}

const goToSettings = () => {
  alert('设置功能开发中...')
}

const goToAbout = () => {
  alert('关于我们功能开发中...')
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  padding-bottom: 80px;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.profile-header {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  padding: 40px 20px 30px;
  display: flex;
  align-items: center;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.avatar-text {
  font-size: 32px;
  font-weight: 600;
  color: white;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin-bottom: 6px;
}

.phone {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.menu-list {
  padding: 16px;
}

.menu-section {
  background-color: white;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.menu-item:active {
  background-color: #f5f5f5;
}

.menu-icon {
  font-size: 22px;
  margin-right: 12px;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  color: #333;
}

.menu-arrow {
  font-size: 20px;
  color: #999;
}

.menu-item.logout {
  color: #ff4d4f;
}

.menu-item.logout .menu-text {
  color: #ff4d4f;
}
</style>
