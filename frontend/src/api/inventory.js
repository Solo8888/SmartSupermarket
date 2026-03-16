import request from './index'

export const getInventories = (params) => {
  return request.get('/inventory', { params })
}

export const getInventory = (productId) => {
  return request.get(`/inventory/${productId}`)
}

export const updateInventory = (productId, data) => {
  return request.put(`/inventory/${productId}`, data)
}

export const stockIn = (productId, data) => {
  return request.post(`/inventory/stock-in/${productId}`, data)
}

export const stockOut = (productId, data) => {
  return request.post(`/inventory/stock-out/${productId}`, data)
}
