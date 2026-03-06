import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))
  const isAuthenticated = ref(!!accessToken.value)

  const login = async (phone, password) => {
    const response = await authApi.login({ phone, password })
    accessToken.value = response.access_token
    userInfo.value = {
      user_id: response.user_id,
      phone: response.phone,
      name: response.name
    }
    isAuthenticated.value = true
    
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('user_info', JSON.stringify(userInfo.value))
    
    return response
  }

  const register = async (username, phone, password, role = 'customer') => {
    const response = await authApi.register({ username, phone, password, role })
    return response
  }

  const logout = () => {
    accessToken.value = ''
    userInfo.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  return {
    accessToken,
    userInfo,
    isAuthenticated,
    login,
    register,
    logout
  }
})
