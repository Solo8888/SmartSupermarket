import request from './index'

export const associationRulesApi = {
  // 获取关联规则
  getAssociationRules(params) {
    return request.get('/analytics/association-rules', { params })
  }
}
