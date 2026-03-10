import request from './index'

export const inventoryApi = {
  getInventories(params) {
    return request.get('/inventory', { params })
  },

  getInventory(productId) {
    return request.get(`/inventory/${productId}`)
  },

  updateInventory(productId, data) {
    return request.put(`/inventory/${productId}`, data)
  },

  stockIn(productId, data) {
    return request.post(`/inventory/stock-in/${productId}`, data)
  },

  stockOut(productId, data) {
    return request.post(`/inventory/stock-out/${productId}`, data)
  }
}
