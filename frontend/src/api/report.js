// 报表相关 API 调用
import axios from './index'

const reportAPI = {
  // 获取推荐转化率分析
  getRecommendationConversion: async (params) => {
    try {
      const response = await axios.get('/reports/recommendation-conversion', {
        params
      })
      return response.data
    } catch (error) {
      console.error('获取推荐转化率分析失败:', error)
      throw error
    }
  },

  // 导出报表
  exportReport: async (data) => {
    try {
      const response = await axios.post('/reports/export', data)
      return response.data
    } catch (error) {
      console.error('导出报表失败:', error)
      throw error
    }
  }
}

export default reportAPI