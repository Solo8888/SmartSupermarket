import request from './index'

export const addToCart = (data) => {
  return request.post('/cart', data)
}

export const getCartItems = () => {
  return request.get('/cart')
}

export const updateCartItem = (id, data) => {
  return request.put(`/cart/${id}`, data)
}

export const removeCartItem = (id) => {
  return request.delete(`/cart/${id}`)
}

export const clearCart = () => {
  return request.delete('/cart')
}