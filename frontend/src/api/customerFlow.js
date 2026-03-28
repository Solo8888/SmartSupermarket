import request from './index'

const customerFlowApi = {
  // 获取客流数据
  getCustomerFlow: async (startTime, endTime, storeId = null) => {
    const params = {
      start_time: startTime,
      end_time: endTime
    }
    if (storeId !== null && storeId !== undefined) {
      params.store_id = storeId
    }
    return await request.get('/customer-flow', { params })
  },

  // 获取预测客流数据
  getForecastData: async (date, storeId = null) => {
    const params = {
      date: date
    }
    if (storeId !== null && storeId !== undefined) {
      params.store_id = storeId
    }
    return await request.get('/analytics/footfall/forecast', { params })
  },

  // 获取时段客流分布
  getTimeDistribution: async (startDate, endDate, storeId = null) => {
    const params = {
      start_date: startDate,
      end_date: endDate
    }
    if (storeId !== null && storeId !== undefined) {
      params.store_id = storeId
    }
    return await request.get('/analytics/footfall/time-distribution', { params })
  },

  // 导出客流分析报告
  exportReport: async (startDate, endDate, format, storeId = null) => {
    const data = {
      start_date: startDate,
      end_date: endDate,
      format: format
    }
    if (storeId !== null && storeId !== undefined) {
      data.store_id = storeId
    }
    return await request.post('/analytics/footfall/export', data, {
      responseType: 'blob'
    })
  },

  // 获取门店列表
  getStores: async () => {
    return await request.get('/stores')
  },

  // 获取本周与上周每小时客流对比
  getWeekComparison: async (storeId = null) => {
    const params = {}
    if (storeId !== null && storeId !== undefined) {
      params.store_id = storeId
    }
    return await request.get('/analytics/footfall/week-comparison', { params })
  },

  // 获取工作日与周末每小时客流对比
  getWeekendWeekdayComparison: async (storeId = null) => {
    const params = {}
    if (storeId !== null && storeId !== undefined) {
      params.store_id = storeId
    }
    return await request.get('/analytics/footfall/weekend-weekday-comparison', { params })
  }
}

export default customerFlowApi