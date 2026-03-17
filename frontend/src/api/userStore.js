import request from './index'

// 用户门店管理API
const userStoreApi = {
  // 分配门店给用户
  createStoreAllocation: async (data) => {
    try {
      return await request({
        url: '/user-store',
        method: 'POST',
        data
      })
    } catch (error) {
      console.error('分配门店失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '分配门店失败，请稍后重试'
      throw new Error(errorMessage)
    }
  },

  // 获取用户的门店列表
  getUserStores: async (userId) => {
    try {
      return await request({
        url: `/user-store/user/${userId}`,
        method: 'GET'
      })
    } catch (error) {
      console.error('获取用户门店列表失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '获取用户门店列表失败，请稍后重试'
      throw new Error(errorMessage)
    }
  },

  // 获取门店的管理员列表
  getStoreUsers: async (storeId) => {
    try {
      return await request({
        url: `/user-store/store/${storeId}`,
        method: 'GET'
      })
    } catch (error) {
      console.error('获取门店管理员列表失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '获取门店管理员列表失败，请稍后重试'
      throw new Error(errorMessage)
    }
  },

  // 取消门店分配
  deleteStoreAllocation: async (allocationId) => {
    try {
      return await request({
        url: `/user-store/${allocationId}`,
        method: 'DELETE'
      })
    } catch (error) {
      console.error('取消门店分配失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '取消门店分配失败，请稍后重试'
      throw new Error(errorMessage)
    }
  }
}

export default userStoreApi