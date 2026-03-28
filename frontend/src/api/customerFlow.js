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

  // 获取门店列表
  getStores: async () => {
    return await request.get('/stores')
  }
}

export default customerFlowApi