import request from './index'

export const productApi = {
  getProducts(params) {
    return request.get('/products', { params })
  },

  getProduct(id) {
    return request.get(`/products/${id}`)
  },

  createProduct(data) {
    return request.post('/products', data)
  },

  updateProduct(id, data) {
    return request.put(`/products/${id}`, data)
  },

  deleteProduct(id) {
    return request.delete(`/products/${id}`)
  }
}
