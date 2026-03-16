import request from './index'

export const getOrders = (params) => {
  return request.get('/orders', { params })
}

export const getOrder = (id) => {
  return request.get(`/orders/${id}`)
}

export const createOrder = (data) => {
  return request.post('/orders', data)
}

export const payOrder = (id, data) => {
  return request.post(`/orders/${id}/pay`, data)
}

export const updateOrderStatus = (id, data) => {
  return request.put(`/orders/${id}/status`, data)
}

export const cancelOrder = (id) => {
  return request.post(`/orders/${id}/cancel`)
}
