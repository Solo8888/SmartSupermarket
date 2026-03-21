import { defineStore } from 'pinia'
import { ref } from 'vue'

// 门店状态管理
export const useStoreStore = defineStore('store', () => {
  // 当前选中的门店
  const selectedStore = ref(JSON.parse(localStorage.getItem('selected_store') || 'null'))
  
  // 门店列表
  const stores = ref([])
  
  // 设置选中的门店
  const setSelectedStore = (store) => {
    selectedStore.value = store
    localStorage.setItem('selected_store', JSON.stringify(store))
  }
  
  // 清除选中的门店
  const clearSelectedStore = () => {
    selectedStore.value = null
    localStorage.removeItem('selected_store')
  }
  
  // 设置门店列表
  const setStores = (storeList) => {
    stores.value = storeList
  }
  
  return {
    selectedStore,
    stores,
    setSelectedStore,
    clearSelectedStore,
    setStores
  }
})
