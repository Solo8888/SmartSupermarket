import request from './index'

// 获取门店列表（分页）
export const getStores = (params) => {
  return request({
    url: '/stores',
    method: 'GET',
    params
  })
}

// 获取所有门店（不分页）
export const getAllStores = () => {
  return request({
    url: '/stores/all',
    method: 'GET'
  })
}

// 获取单个门店详情
export const getStore = (id) => {
  return request({
    url: `/stores/${id}`,
    method: 'GET'
  })
}

// 创建门店
export const createStore = (data) => {
  return request({
    url: '/stores',
    method: 'POST',
    data
  })
}

// 更新门店
export const updateStore = (id, data) => {
  return request({
    url: `/stores/${id}`,
    method: 'PUT',
    data
  })
}

// 删除门店
export const deleteStore = (id) => {
  return request({
    url: `/stores/${id}`,
    method: 'DELETE'
  })
}
