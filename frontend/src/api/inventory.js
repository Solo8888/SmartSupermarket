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

// 库存优化相关API
export const getReplenishmentSuggestions = (params) => {
  return request.get('/inventory/optimization/replenishment', { params })
}

export const getTransferPlans = (params) => {
  return request.get('/inventory/optimization/transfer', { params })
}

export const updateThreshold = (productId, data) => {
  return request.put(`/inventory/optimization/threshold/${productId}`, data)
}
