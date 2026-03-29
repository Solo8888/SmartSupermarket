// 用户画像相关 API 调用
import axios from './index'

const userProfileAPI = {
  // 获取用户标签体系
  getUserTags: async () => {
    try {
      const response = await axios.get('/analytics/user-tags')
      return response
    } catch (error) {
      console.error('获取用户标签失败:', error)
      throw error
    }
  },

  // 获取用户群体分类
  getUserSegments: async () => {
    try {
      const response = await axios.get('/analytics/user-segments')
      return response
    } catch (error) {
      console.error('获取用户群体失败:', error)
      throw error
    }
  },

  // 获取群体详情
  getSegmentDetail: async (segmentId) => {
    try {
      const response = await axios.get(`/analytics/user-segments/${segmentId}`)
      return response
    } catch (error) {
      console.error('获取群体详情失败:', error)
      throw error
    }
  }
}

export default userProfileAPI