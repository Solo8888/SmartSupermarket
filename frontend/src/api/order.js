import request from './index'

export const orderApi = {
  getOrders(params) {
    return request.get('/orders', { params })
  },

  getOrder(id) {
    return request.get(`/orders/${id}`)
  },

  createOrder(data) {
    return request.post('/orders', data)
  },

  payOrder(id, data) {
    return request.post(`/orders/${id}/pay`, data)
  },

  updateOrderStatus(id, data) {
    return request.put(`/orders/${id}/status`, data)
  },

  cancelOrder(id) {
    return request.post(`/orders/${id}/cancel`)
  }
}
