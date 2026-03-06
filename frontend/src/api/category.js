import request from './index'

export const categoryApi = {
  getCategories(params = {}) {
    return request({
      url: '/categories',
      method: 'get',
      params
    })
  },
  
  getCategory(categoryId) {
    return request({
      url: `/categories/${categoryId}`,
      method: 'get'
    })
  },
  
  createCategory(data) {
    return request({
      url: '/categories',
      method: 'post',
      data
    })
  },
  
  updateCategory(categoryId, data) {
    return request({
      url: `/categories/${categoryId}`,
      method: 'put',
      data
    })
  },
  
  deleteCategory(categoryId) {
    return request({
      url: `/categories/${categoryId}`,
      method: 'delete'
    })
  }
}
