<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { computed } from 'vue'

const router = useRouter()
const userStore = useUserStore()

const isInventoryManager = computed(() => {
  return userStore.userInfo?.role === 'inventory_manager'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const goToAdmin = () => {
  router.push('/admin/categories')
}
</script>

<template>
  <div class="home-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">智能超市管理系统</h1>
        <div class="user-info">
          <span>欢迎，{{ userStore.userInfo?.name || userStore.userInfo?.phone }}</span>
          <button @click="handleLogout" class="logout-button">退出登录</button>
        </div>
      </div>
    </header>
    
    <main class="main">
      <div class="welcome-card">
        <h2>登录成功！</h2>
        <p>欢迎使用智能超市管理系统</p>
        <div class="user-details">
          <p><strong>用户ID:</strong> {{ userStore.userInfo?.user_id }}</p>
          <p><strong>手机号:</strong> {{ userStore.userInfo?.phone }}</p>
          <p><strong>角色:</strong> {{ userStore.userInfo?.role === 'inventory_manager' ? '库存管理员' : '顾客' }}</p>
        </div>
        
        <div v-if="isInventoryManager" class="admin-section">
          <button class="btn-admin" @click="goToAdmin">
            进入管理后台
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info span {
  font-size: 16px;
}

.logout-button {
  padding: 8px 20px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
}

.welcome-card {
  background: white;
  padding: 48px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.welcome-card h2 {
  color: #333;
  font-size: 32px;
  margin-bottom: 16px;
}

.welcome-card p {
  color: #666;
  font-size: 18px;
  margin-bottom: 32px;
}

.user-details {
  background-color: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.user-details p {
  color: #555;
  font-size: 16px;
  margin: 12px 0;
}

.admin-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-admin {
  padding: 14px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.btn-admin:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 12px;
    padding: 0 16px;
  }

  .logo {
    font-size: 20px;
  }

  .user-info {
    flex-direction: column;
    gap: 10px;
  }

  .user-info span {
    font-size: 14px;
  }

  .logout-button {
    padding: 6px 16px;
    font-size: 13px;
  }

  .main {
    padding: 32px 16px;
  }

  .welcome-card {
    padding: 32px 24px;
  }

  .welcome-card h2 {
    font-size: 26px;
  }

  .welcome-card p {
    font-size: 16px;
  }

  .user-details {
    padding: 20px;
  }

  .user-details p {
    font-size: 15px;
  }
  
  .admin-section {
    margin-top: 24px;
    padding-top: 20px;
  }
  
  .btn-admin {
    padding: 12px 24px;
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 12px 0;
  }

  .logo {
    font-size: 18px;
  }

  .main {
    padding: 24px 12px;
  }

  .welcome-card {
    padding: 24px 20px;
    border-radius: 10px;
  }

  .welcome-card h2 {
    font-size: 22px;
    margin-bottom: 12px;
  }

  .welcome-card p {
    font-size: 15px;
    margin-bottom: 24px;
  }

  .user-details {
    padding: 16px;
  }

  .user-details p {
    font-size: 14px;
    margin: 10px 0;
  }
  
  .admin-section {
    margin-top: 20px;
    padding-top: 16px;
  }
  
  .btn-admin {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
