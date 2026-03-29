<template>
  <div class="customer-flow-container">
    <el-row :gutter="20" class="mb-4">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <span>客流趋势</span>
          </template>
          <div class="chart-container">
            <div ref="trendChart" class="chart"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
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
      </el-col>
    </el-row>

    <el-card shadow="hover" class="mb-4">
      <template #header>
        <div class="card-header-with-date">
          <span>时段客流分布</span>
          <div class="header-actions">
            <el-date-picker
              v-model="distributionDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              @change="handleDistributionDateChange"
              size="small"
              style="width: 150px;"
            />
            <el-dropdown trigger="click" class="ml-2">
              <el-button size="small" type="primary" :icon="Download">
                导出
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleDistributionExport('excel')">
                    Excel
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleDistributionExport('pdf')">
                    PDF
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>
      <div class="chart-container">
        <div ref="distributionChart" class="chart"></div>
      </div>
    </el-card>

    <el-card shadow="hover" class="mb-4">
      <template #header>
        <span>本周与上周每小时客流对比</span>
      </template>
      <div class="chart-container">
        <div ref="weekComparisonChart" class="chart"></div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <span>工作日与周末客流对比</span>
      </template>
      <div class="chart-container">
        <div ref="weekendWeekdayChart" class="chart"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import * as echarts from 'echarts'
import { Refresh, Download, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import customerFlowApi from '../../api/customerFlow'
import userStoreApi from '../../api/userStore'
import { useUserStore } from '../../stores/user'

// 用户状态
const userStore = useUserStore()

// 响应式数据
const selectedDate = ref('')
const distributionDate = ref('')
const selectedStoreId = ref('')
const currentStoreName = ref('')
const customerFlowData = ref([])
const forecastData = ref([])
const timeDistributionData = ref([])
const weekComparisonData = ref([])
const weekendWeekdayData = ref([])
const trendChart = ref(null)
const distributionChart = ref(null)
const weekComparisonChart = ref(null)
const weekendWeekdayChart = ref(null)
const trendChartInstance = ref(null)
const distributionChartInstance = ref(null)
const weekComparisonChartInstance = ref(null)
const weekendWeekdayChartInstance = ref(null)

// 计算属性
const totalCustomers = computed(() => {
  if (!timeDistributionData.value || timeDistributionData.value.length === 0) return 0
  return timeDistributionData.value.reduce((sum, item) => sum + item.count, 0)
})

const averageCustomersPerHour = computed(() => {
  if (!timeDistributionData.value || timeDistributionData.value.length === 0) return 0
  return Math.round(totalCustomers.value / timeDistributionData.value.length)
})

const peakHour = computed(() => {
  if (!timeDistributionData.value || timeDistributionData.value.length === 0) return null
  const peak = timeDistributionData.value.reduce((max, item) => 
    item.count > max.count ? item : max
  )
  return peak.hour
})

const lowHour = computed(() => {
  if (!timeDistributionData.value || timeDistributionData.value.length === 0) return null
  const low = timeDistributionData.value.reduce((min, item) => 
    item.count < min.count ? item : min
  )
  return low.hour
})

const peakHourValue = computed(() => {
  return peakHour.value || '暂无数据'
})

const lowHourValue = computed(() => {
  return lowHour.value || '暂无数据'
})

// 方法
const loadUserStore = async () => {
  try {
    const userInfo = userStore.userInfo
    if (!userInfo || !userInfo.user_id) {
      console.error('未获取到用户信息')
      return
    }
    
    // 获取当前用户管理的门店
    const response = await userStoreApi.getUserStores(userInfo.user_id)
    const stores = response.data || response
    
    if (stores && stores.length > 0) {
      // 使用第一个门店
      selectedStoreId.value = stores[0].store_id
      currentStoreName.value = stores[0].store_name || stores[0].name || '未知门店'
      loadCustomerFlowData()
      loadDistributionData()
      loadComparisonData()
    } else {
      console.error('当前用户没有管理的门店')
      ElMessage.warning('您没有管理的门店，请联系管理员分配门店')
    }
  } catch (error) {
    console.error('加载用户门店失败:', error)
    ElMessage.error('加载门店信息失败')
  }
}

const loadCustomerFlowData = async () => {
  if (!selectedDate.value) return
  
  try {
    const date = selectedDate.value
    
    // 加载客流趋势数据（当天实际数据）
    const flowResponse = await customerFlowApi.getCustomerFlow(
      `${date} 00:00:00`,
      `${date} 23:59:59`,
      selectedStoreId.value
    )
    customerFlowData.value = Array.isArray(flowResponse.data) ? flowResponse.data : []
    
    // 加载预测数据
    const forecastResponse = await customerFlowApi.getForecastData(
      date,
      selectedStoreId.value
    )
    forecastData.value = Array.isArray(forecastResponse.data) ? forecastResponse.data : []
    
    updateCharts()
  } catch (error) {
    console.error('加载客流数据失败:', error)
    customerFlowData.value = []
    forecastData.value = []
  }
}

const loadDistributionData = async () => {
  if (!distributionDate.value) return
  
  try {
    const date = distributionDate.value
    
    // 加载时段客流分布数据
    const distributionResponse = await customerFlowApi.getTimeDistribution(
      date,
      date,
      selectedStoreId.value
    )
    timeDistributionData.value = Array.isArray(distributionResponse.data) ? distributionResponse.data : []
    
    updateDistributionChart()
  } catch (error) {
    console.error('加载时段分布数据失败:', error)
    timeDistributionData.value = []
  }
}

const loadComparisonData = async () => {
  try {
    // 加载本周与上周每小时客流对比数据
    const weekComparisonResponse = await customerFlowApi.getWeekComparison(selectedStoreId.value)
    weekComparisonData.value = Array.isArray(weekComparisonResponse.data) ? weekComparisonResponse.data : []
    
    // 加载工作日与周末每小时客流对比数据
    const weekendWeekdayResponse = await customerFlowApi.getWeekendWeekdayComparison(selectedStoreId.value)
    weekendWeekdayData.value = Array.isArray(weekendWeekdayResponse.data) ? weekendWeekdayResponse.data : []
    
    updateComparisonCharts()
  } catch (error) {
    console.error('加载对比数据失败:', error)
    weekComparisonData.value = []
    weekendWeekdayData.value = []
  }
}

const updateCharts = () => {
  updateTrendChart()
  updateDistributionChart()
}

const updateComparisonCharts = () => {
  updateWeekComparisonChart()
  updateWeekendWeekdayChart()
}

const updateTrendChart = () => {
  if (!trendChart.value) return
  
  if (trendChartInstance.value) {
    trendChartInstance.value.dispose()
  }
  
  trendChartInstance.value = echarts.init(trendChart.value)
  
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  
  // 实际数据
  const customerData = hours.map(hour => {
    const hourNum = parseInt(hour.split(':')[0])
    if (!customerFlowData.value || !Array.isArray(customerFlowData.value)) {
      return null
    }
    const item = customerFlowData.value.find(data => data.hour === hourNum)
    return item ? item.customer_count : null
  })
  
  // 预测数据
  const forecastDataArray = hours.map(hour => {
    const hourNum = parseInt(hour.split(':')[0])
    if (!forecastData.value || !Array.isArray(forecastData.value)) {
      return null
    }
    const item = forecastData.value.find(data => data.hour === hourNum)
    return item ? item.forecast_count : null
  })
  
  const option = {
    title: {
      text: '24小时客流趋势（含预测）',
      left: 'center'
    },
    grid: {
      top: 80,
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
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
    legend: {
      data: ['实际客流', '预测客流'],
      top: 40
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
        name: '实际客流',
        type: 'line',
        data: customerData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#5470c6'
        },
        itemStyle: {
          color: '#5470c6'
        },
        areaStyle: {
          opacity: 0.3,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5470c6' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
          ])
        }
      },
      {
        name: '预测客流',
        type: 'line',
        data: forecastDataArray,
        smooth: true,
        lineStyle: {
          width: 2,
          type: 'dashed',
          color: '#91cc75'
        },
        itemStyle: {
          color: '#91cc75'
        },
        areaStyle: {
          opacity: 0.1,
          color: '#91cc75'
        }
      }
    ]
  }
  
  trendChartInstance.value.setOption(option)
}

const updateDistributionChart = () => {
  if (!distributionChart.value) return
  
  if (distributionChartInstance.value) {
    distributionChartInstance.value.dispose()
  }
  
  distributionChartInstance.value = echarts.init(distributionChart.value)
  
  const hours = timeDistributionData.value.map(item => `${item.hour}:00`)
  const counts = timeDistributionData.value.map(item => item.count)
  
  const option = {
    title: {
      text: `时段客流分布 (${distributionDate.value || '请选择日期'})`,
      left: 'center'
    },
    grid: {
      top: 80,
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '客流量'
    },
    series: [
      {
        name: '客流量',
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 2,
          color: '#5470c6'
        },
        itemStyle: {
          color: '#5470c6'
        },
        areaStyle: {
          opacity: 0.2,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5470c6' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
          ])
        }
      }
    ]
  }
  
  distributionChartInstance.value.setOption(option)
}

const updateWeekComparisonChart = () => {
  if (!weekComparisonChart.value) return
  
  if (weekComparisonChartInstance.value) {
    weekComparisonChartInstance.value.dispose()
  }
  
  weekComparisonChartInstance.value = echarts.init(weekComparisonChart.value)
  
  const hours = weekComparisonData.value.map(item => item.hour)
  const thisWeekData = weekComparisonData.value.map(item => item.this_week)
  const lastWeekData = weekComparisonData.value.map(item => item.last_week)
  
  const option = {
    title: {
      text: '本周与上周每小时客流对比',
      left: 'center'
    },
    grid: {
      top: 100,
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['本周', '上周'],
      top: 40
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '客流量'
    },
    series: [
      {
        name: '本周',
        type: 'line',
        data: thisWeekData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#5470c6'
        },
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '上周',
        type: 'line',
        data: lastWeekData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#91cc75'
        },
        itemStyle: {
          color: '#91cc75'
        }
      }
    ]
  }
  
  weekComparisonChartInstance.value.setOption(option)
}

const updateWeekendWeekdayChart = () => {
  if (!weekendWeekdayChart.value) return
  
  if (weekendWeekdayChartInstance.value) {
    weekendWeekdayChartInstance.value.dispose()
  }
  
  weekendWeekdayChartInstance.value = echarts.init(weekendWeekdayChart.value)
  
  const hours = weekendWeekdayData.value.map(item => item.hour)
  const thisWeekWeekdayData = weekendWeekdayData.value.map(item => item.this_week_weekday)
  const thisWeekWeekendData = weekendWeekdayData.value.map(item => item.this_week_weekend)
  const lastWeekWeekdayData = weekendWeekdayData.value.map(item => item.last_week_weekday)
  const lastWeekWeekendData = weekendWeekdayData.value.map(item => item.last_week_weekend)
  
  const option = {
    title: {
      text: '工作日与周末每小时客流对比',
      left: 'center'
    },
    grid: {
      top: 100,
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['本周-工作日', '本周-周末', '上周-工作日', '上周-周末'],
      top: 40
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '客流量'
    },
    series: [
      {
        name: '本周-工作日',
        type: 'line',
        data: thisWeekWeekdayData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#5470c6'
        },
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '本周-周末',
        type: 'line',
        data: thisWeekWeekendData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#91cc75'
        },
        itemStyle: {
          color: '#91cc75'
        }
      },
      {
        name: '上周-工作日',
        type: 'line',
        data: lastWeekWeekdayData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#fac858'
        },
        itemStyle: {
          color: '#fac858'
        }
      },
      {
        name: '上周-周末',
        type: 'line',
        data: lastWeekWeekendData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#ee6666'
        },
        itemStyle: {
          color: '#ee6666'
        }
      }
    ]
  }
  
  weekendWeekdayChartInstance.value.setOption(option)
}

const handleDateChange = () => {
  loadCustomerFlowData()
}

const handleDistributionDateChange = () => {
  loadDistributionData()
}



const refreshData = () => {
  loadCustomerFlowData()
  loadComparisonData()
}

const handleExport = async (format) => {
  try {
    const date = selectedDate.value
    const response = await customerFlowApi.exportReport(
      date,
      date,
      format,
      selectedStoreId.value
    )
    
    // 创建下载链接
    const blob = new Blob([response], { 
      type: format === 'pdf' ? 'application/pdf' : 'text/csv' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `footfall_report_${date}.${format === 'pdf' ? 'pdf' : 'csv'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  }
}

const handleDistributionExport = async (format) => {
  try {
    const date = distributionDate.value
    if (!date) {
      ElMessage.warning('请选择日期')
      return
    }
    
    const response = await customerFlowApi.exportReport(
      date,
      date,
      format,
      selectedStoreId.value
    )
    
    // 创建下载链接
    let contentType = ''
    let extension = ''
    if (format === 'pdf') {
      contentType = 'application/pdf'
      extension = 'pdf'
    } else if (format === 'excel') {
      contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      extension = 'xlsx'
    }
    
    const blob = new Blob([response], { type: contentType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `distribution_report_${date}.${extension}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('时段客流分布导出成功')
  } catch (error) {
    console.error('导出时段客流分布失败:', error)
    ElMessage.error('导出失败')
  }
}

// 生命周期
onMounted(() => {
  // 设置默认日期为今天
  const today = new Date()
  const todayStr = today.toISOString().split('T')[0]
  selectedDate.value = todayStr
  distributionDate.value = todayStr
  
  // 加载用户门店并自动选择
  loadUserStore()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (trendChartInstance.value) {
      trendChartInstance.value.resize()
    }
    if (distributionChartInstance.value) {
      distributionChartInstance.value.resize()
    }
    if (weekComparisonChartInstance.value) {
      weekComparisonChartInstance.value.resize()
    }
    if (weekendWeekdayChartInstance.value) {
      weekendWeekdayChartInstance.value.resize()
    }
  })
})

// 监听数据变化，更新图表
watch([customerFlowData, timeDistributionData], () => {
  updateCharts()
}, { deep: true })

watch([weekComparisonData, weekendWeekdayData], () => {
  updateComparisonCharts()
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

.header-actions {
  display: flex;
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
  grid-template-columns: repeat(2, 1fr);
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

.ml-2 {
  margin-left: 8px;
}

.card-header-with-date {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
