<template>
  <div class="customer-flow-container">
    <el-card shadow="hover" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>客流数据分析</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="mb-4">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="门店">
          <el-select v-model="selectedStoreId" placeholder="选择门店" @change="handleStoreChange">
            <el-option
              v-for="store in stores"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="mb-4">
      <template #header>
        <span>客流趋势</span>
      </template>
      <div class="chart-container">
        <div ref="trendChart" class="chart"></div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <span>客流统计</span>
      </template>
      <div class="stats-grid">
        <el-statistic class="stat-item" title="总客流量" :value="totalCustomers" />
        <el-statistic class="stat-item" title="平均每小时客流" :value="averageCustomersPerHour" />
        <el-statistic class="stat-item" title="高峰时段" :value="peakHourValue" />
        <el-statistic class="stat-item" title="低谷时段" :value="lowHourValue" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import * as echarts from 'echarts'
import { Refresh } from '@element-plus/icons-vue'
import customerFlowApi from '../../api/customerFlow'

// 响应式数据
const dateRange = ref([])
const selectedStoreId = ref('')
const stores = ref([])
const customerFlowData = ref([])
const trendChart = ref(null)
const chartInstance = ref(null)

// 计算属性
const totalCustomers = computed(() => {
  if (!customerFlowData.value || customerFlowData.value.length === 0) return 0
  return customerFlowData.value.reduce((sum, item) => sum + item.customer_count, 0)
})

const averageCustomersPerHour = computed(() => {
  if (!customerFlowData.value || customerFlowData.value.length === 0) return 0
  return Math.round(totalCustomers.value / customerFlowData.value.length)
})

const peakHour = computed(() => {
  if (!customerFlowData.value || customerFlowData.value.length === 0) return null
  const peak = customerFlowData.value.reduce((max, item) => 
    item.customer_count > max.customer_count ? item : max
  )
  return `${peak.hour}:00`
})

const lowHour = computed(() => {
  if (!customerFlowData.value || customerFlowData.value.length === 0) return null
  const low = customerFlowData.value.reduce((min, item) => 
    item.customer_count < min.customer_count ? item : min
  )
  return `${low.hour}:00`
})

// 用于el-statistic的数值（字符串会被转换为0显示）
const peakHourValue = computed(() => {
  return peakHour.value || 0
})

const lowHourValue = computed(() => {
  return lowHour.value || 0
})

// 方法
const loadStores = async () => {
  try {
    const data = await customerFlowApi.getStores()
    // 检查是否是分页数据
    if (data.items) {
      stores.value = data.items
    } else {
      stores.value = data
    }
    if (stores.value.length > 0) {
      selectedStoreId.value = stores.value[0].id
      // 加载客流数据
      loadCustomerFlowData()
    }
  } catch (error) {
    console.error('加载门店失败:', error)
  }
}

const loadCustomerFlowData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) return
  
  try {
    const [startDate, endDate] = dateRange.value
    const response = await customerFlowApi.getCustomerFlow(
      `${startDate} 00:00:00`,
      `${endDate} 23:59:59`,
      selectedStoreId.value
    )
    // 处理后端返回的数据格式，确保始终是数组
    customerFlowData.value = Array.isArray(response.data) ? response.data : []
    updateChart()
  } catch (error) {
    console.error('加载客流数据失败:', error)
    // 发生错误时，重置为数组
    customerFlowData.value = []
  }
}

const updateChart = () => {
  if (!trendChart.value) return
  
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  
  chartInstance.value = echarts.init(trendChart.value)
  
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const customerData = hours.map(hour => {
    const hourNum = parseInt(hour.split(':')[0])
    if (!customerFlowData.value || !Array.isArray(customerFlowData.value)) {
      return 0
    }
    const item = customerFlowData.value.find(data => data.hour === hourNum)
    return item ? item.customer_count : 0
  })
  
  const option = {
    title: {
      text: '24小时客流趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hours
    },
    yAxis: {
      type: 'value',
      name: '客流量'
    },
    series: [
      {
        name: '客流量',
        type: 'line',
        data: customerData,
        smooth: true,
        lineStyle: {
          width: 2
        },
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
}

const handleDateChange = () => {
  loadCustomerFlowData()
}

const handleStoreChange = () => {
  loadCustomerFlowData()
}

const refreshData = () => {
  loadCustomerFlowData()
}

// 生命周期
onMounted(() => {
  // 设置默认时间范围为最近7天
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 7)
  
  dateRange.value = [
    startDate.toISOString().split('T')[0],
    endDate.toISOString().split('T')[0]
  ]
  
  loadStores()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (chartInstance.value) {
      chartInstance.value.resize()
    }
  })
})

// 监听数据变化，更新图表
watch(customerFlowData, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.customer-flow-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.mb-4 {
  margin-bottom: 20px;
}
</style>