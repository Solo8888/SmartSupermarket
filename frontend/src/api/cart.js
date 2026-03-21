import request from './index'

export const addToCart = (data) => {
  return request.post('/api/cart/add', data)
}

export const getCartItems = () => {
  return request.get('/api/cart')
}

export const updateCartItem = (id, data) => {
  return request.put(`/api/cart/items/${id}`, data)
}

export const removeCartItem = (id) => {
  return request.delete(`/api/cart/items/${id}`)
}

export const clearCart = () => {
  return request.delete('/api/cart')
}