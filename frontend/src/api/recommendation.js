// 推荐系统API
// 处理个性化商品推荐相关的API调用

import axios from 'axios'

const API_BASE_URL = '/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 推荐API
const recommendationApi = {
  /**
   * 获取个性化推荐
   * @param {Object} params - 请求参数
   * @param {string} params.store_id - 门店ID（可选）
   * @param {number} params.limit - 推荐商品数量限制
   * @returns {Promise} - 推荐结果
   */
  getPersonalizedRecommendations: async (params) => {
    try {
      const response = await api.post('/recommendations/personalized', params)
      return response.data
    } catch (error) {
      console.error('获取个性化推荐失败:', error)
      // 如果个性化推荐失败，返回新用户推荐
      return recommendationApi.getNewUserRecommendations(params)
    }
  },

  /**
   * 获取新用户推荐
   * @param {Object} params - 请求参数
   * @param {string} params.store_id - 门店ID（可选）
   * @param {number} params.limit - 推荐商品数量限制
   * @returns {Promise} - 推荐结果
   */
  getNewUserRecommendations: async (params) => {
    try {
      const { store_id, limit } = params
      const queryParams = new URLSearchParams()
      if (store_id) {
        queryParams.append('store_id', store_id)
      }
      if (limit) {
        queryParams.append('limit', limit)
      }
      const response = await api.get(`/recommendations/new-user?${queryParams.toString()}`)
      return response.data
    } catch (error) {
      console.error('获取新用户推荐失败:', error)
      throw error
    }
  }
}

export default recommendationApi