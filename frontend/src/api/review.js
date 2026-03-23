import request from './index'

export const createReview = (data) => {
  return request.post('/reviews', data)
}

export const getReviewsByProduct = (productId, params) => {
  return request.get(`/reviews/product/${productId}`, { params })
}

export const getReviewsByUser = (params) => {
  return request.get('/reviews/user', { params })
}

export const autoReview = () => {
  return request.post('/reviews/auto')
}
