import request from './index'

export const promotionApi = {
  getPromotions(params) {
    return request.get('/promotions', { params })
  },

  getPromotion(id) {
    return request.get(`/promotions/${id}`)
  },

  createPromotion(data) {
    return request.post('/promotions', data)
  },

  updatePromotion(id, data) {
    return request.put(`/promotions/${id}`, data)
  },

  deletePromotion(id) {
    return request.delete(`/promotions/${id}`)
  }
}
