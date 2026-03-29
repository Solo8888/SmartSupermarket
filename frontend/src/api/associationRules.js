import request from './index'

export const associationRulesApi = {
  // 获取关联规则
  getAssociationRules(params) {
    return request.get('/analytics/association-rules', { params })
  },
  
  // 导出关联规则
  exportAssociationRules(params) {
    return request.get('/analytics/association-rules/export', { 
      params, 
      responseType: 'blob' 
    })
  }
}
