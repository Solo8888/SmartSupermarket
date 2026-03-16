import request from './index'

export const getCategories = (params = {}) => {
  return request({
    url: '/categories',
    method: 'get',
    params
  })
}

export const getAllCategories = () => {
  return request({
    url: '/categories/all',
    method: 'get'
  })
}

export const getCategory = (categoryId) => {
  return request({
    url: `/categories/${categoryId}`,
    method: 'get'
  })
}

export const createCategory = (data) => {
  return request({
    url: '/categories',
    method: 'post',
    data
  })
}

export const updateCategory = (categoryId, data) => {
  return request({
    url: `/categories/${categoryId}`,
    method: 'put',
    data
  })
}

export const deleteCategory = (categoryId) => {
  return request({
    url: `/categories/${categoryId}`,
    method: 'delete'
  })
}
