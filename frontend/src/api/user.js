import request from './index'

// 用户管理API
const userApi = {
  // 获取用户列表
  getUserList: async () => {
    try {
      return await request({
        url: '/users/',
        method: 'GET'
      })
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    }
  },

  // 更新用户角色
  updateUserRole: async (userId, role) => {
    try {
      return await request({
        url: `/users/${userId}/role`,
        method: 'PUT',
        data: { role }
      })
    } catch (error) {
      console.error('更新用户角色失败:', error)
      throw error
    }
  }
}

export default userApi