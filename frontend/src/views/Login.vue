<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const phone = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!phone.value || !password.value) {
    error.value = '请输入手机号和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await userStore.login(phone.value, password.value)
    if (response.role === 'inventory_manager') {
      router.push('/admin/categories')
    } else {
      router.push('/home')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查手机号和密码'
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">智能超市管理系统</h1>
      <h2 class="subtitle">用户登录</h2>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="phone">手机号</label>
          <input
            id="phone"
            v-model="phone"
            type="text"
            placeholder="请输入手机号"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="register-link">
        还没有账号？<a href="#" @click.prevent="goToRegister">立即注册</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 8px;
  font-size: 24px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 32px;
  font-size: 18px;
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #555;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  padding: 8px;
  background-color: #fee;
  border-radius: 4px;
}

.login-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.login-button:hover:not(:disabled) {
  opacity: 0.9;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 14px;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.register-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-container {
    padding: 16px;
  }

  .login-card {
    padding: 24px;
    border-radius: 10px;
  }

  .title {
    font-size: 20px;
  }

  .subtitle {
    font-size: 16px;
    margin-bottom: 24px;
  }

  .login-form {
    gap: 16px;
  }

  .form-group input {
    padding: 10px 14px;
    font-size: 15px;
  }

  .login-button {
    padding: 12px;
    font-size: 15px;
  }

  .register-link {
    margin-top: 20px;
    font-size: 13px;
  }
}

@media (max-width: 360px) {
  .login-card {
    padding: 20px;
  }

  .title {
    font-size: 18px;
  }

  .subtitle {
    font-size: 14px;
    margin-bottom: 20px;
  }

  .form-group label {
    font-size: 13px;
  }

  .form-group input {
    padding: 9px 12px;
    font-size: 14px;
  }

  .login-button {
    padding: 11px;
    font-size: 14px;
  }

  .error-message {
    font-size: 13px;
    padding: 6px;
  }
}
</style>
