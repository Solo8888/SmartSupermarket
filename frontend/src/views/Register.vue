<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  if (!username.value || !phone.value || !password.value || !confirmPassword.value) {
    error.value = '请填写所有必填项'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  if (password.value.length < 6) {
    error.value = '密码长度不能少于6位'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    await userStore.register(username.value, phone.value, password.value, 'customer')
    success.value = '注册成功！即将跳转到登录页...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">智能超市管理系统</h1>
      <h2 class="subtitle">用户注册</h2>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            :disabled="loading"
          />
        </div>
        
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
            placeholder="请输入密码（至少6位）"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
        
        <button type="submit" class="register-button" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="login-link">
        已有账号？<a href="#" @click.prevent="goToLogin">立即登录</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.success-message {
  color: #27ae60;
  font-size: 14px;
  text-align: center;
  padding: 8px;
  background-color: #efe;
  border-radius: 4px;
}

.register-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
  margin-top: 8px;
}

.register-button:hover:not(:disabled) {
  opacity: 0.9;
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-container {
    padding: 16px;
  }

  .register-card {
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

  .register-form {
    gap: 14px;
  }

  .form-group input {
    padding: 10px 14px;
    font-size: 15px;
  }

  .register-button {
    padding: 12px;
    font-size: 15px;
  }

  .login-link {
    margin-top: 20px;
    font-size: 13px;
  }
}

@media (max-width: 360px) {
  .register-card {
    padding: 20px;
  }

  .title {
    font-size: 18px;
  }

  .subtitle {
    font-size: 14px;
    margin-bottom: 20px;
  }

  .register-form {
    gap: 12px;
  }

  .form-group label {
    font-size: 13px;
  }

  .form-group input {
    padding: 9px 12px;
    font-size: 14px;
  }

  .register-button {
    padding: 11px;
    font-size: 14px;
  }

  .error-message,
  .success-message {
    font-size: 13px;
    padding: 6px;
  }
}
</style>
