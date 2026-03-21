import request from './index'

export const getProducts = (params) => {
  return request.get('/products', { params })
}

export const getAllProducts = () => {
  return request.get('/products/all')
}

export const getProduct = (id) => {
  return request.get(`/products/${id}`)
}

export const createProduct = (data) => {
  return request.post('/products', data)
}

export const updateProduct = (id, data) => {
  return request.put(`/products/${id}`, data)
}

export const deleteProduct = (id) => {
  return request.delete(`/products/${id}`)
}

export const getProductsByCategory = (categoryId, params) => {
  return request.get(`/products/category/${categoryId}`, { params })
}
