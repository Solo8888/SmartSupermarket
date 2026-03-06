import request from './index'

export const authApi = {
  login(data) {
    return request({
      url: '/users/login',
      method: 'post',
      data
    })
  },
  
  register(data) {
    return request({
      url: '/users/register',
      method: 'post',
      data
    })
  },
  
  changePassword(data) {
    return request({
      url: '/users/change-password',
      method: 'post',
      data
    })
  }
}
