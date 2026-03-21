import request from './index';

// 获取地址列表
export const getAddresses = async () => {
  try {
    const response = await request.get('/addresses');
    return response;
  } catch (error) {
    console.error('获取地址列表失败:', error);
    throw error;
  }
};

// 添加地址
export const createAddress = async (addressData) => {
  try {
    const response = await request.post('/addresses', addressData);
    return response;
  } catch (error) {
    console.error('添加地址失败:', error);
    throw error;
  }
};

// 更新地址
export const updateAddress = async (addressId, addressData) => {
  try {
    const response = await request.put(`/addresses/${addressId}`, addressData);
    return response;
  } catch (error) {
    console.error('更新地址失败:', error);
    throw error;
  }
};

// 删除地址
export const deleteAddress = async (addressId) => {
  try {
    const response = await request.delete(`/addresses/${addressId}`);
    return response;
  } catch (error) {
    console.error('删除地址失败:', error);
    throw error;
  }
};

// 设置默认地址
export const setDefaultAddress = async (addressId) => {
  try {
    const response = await request.post(`/addresses/${addressId}/default`);
    return response;
  } catch (error) {
    console.error('设置默认地址失败:', error);
    throw error;
  }
};