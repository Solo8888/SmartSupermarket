<template>
  <div class="customer-flow-container">
    <el-card shadow="hover" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>客流数据分析</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
            <el-dropdown @command="handleExport" class="ml-2">
              <el-button type="success" size="small">
                <el-icon><Download /></el-icon>
                导出报告
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">导出为 Excel</el-dropdown-item>
                  <el-dropdown-item command="pdf">导出为 PDF</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
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
          <el-select v-model="selectedStoreId" placeholder="选择门店" clearable @change="handleStoreChange">
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

    <el-card shadow="hover">
      <template #header>
        <span>时段客流分布</span>
      </template>
      <div class="chart-container">
        <div ref="distributionChart" class="chart"></div>
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

// 响应式数据
const dateRange = ref([])
const selectedStoreId = ref('')
const stores = ref([])
const customerFlowData = ref([])
const timeDistributionData = ref([])
const trendChart = ref(null)
const distributionChart = ref(null)
const trendChartInstance = ref(null)
const distributionChartInstance = ref(null)

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
const loadStores = async () => {
  try {
    const data = await customerFlowApi.getStores()
    if (data.items) {
      stores.value = data.items
    } else {
      stores.value = data
    }
    if (stores.value.length > 0) {
      selectedStoreId.value = stores.value[0].id
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
    
    // 加载客流趋势数据
    const flowResponse = await customerFlowApi.getCustomerFlow(
      `${startDate} 00:00:00`,
      `${endDate} 23:59:59`,
      selectedStoreId.value
    )
    customerFlowData.value = Array.isArray(flowResponse.data) ? flowResponse.data : []
    
    // 加载时段客流分布数据
    const distributionResponse = await customerFlowApi.getTimeDistribution(
      startDate,
      endDate,
      selectedStoreId.value
    )
    timeDistributionData.value = Array.isArray(distributionResponse.data) ? distributionResponse.data : []
    
    updateCharts()
  } catch (error) {
    console.error('加载客流数据失败:', error)
    customerFlowData.value = []
    timeDistributionData.value = []
  }
}

const updateCharts = () => {
  updateTrendChart()
  updateDistributionChart()
}

const updateTrendChart = () => {
  if (!trendChart.value) return
  
  if (trendChartInstance.value) {
    trendChartInstance.value.dispose()
  }
  
  trendChartInstance.value = echarts.init(trendChart.value)
  
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
  
  trendChartInstance.value.setOption(option)
}

const updateDistributionChart = () => {
  if (!distributionChart.value) return
  
  if (distributionChartInstance.value) {
    distributionChartInstance.value.dispose()
  }
  
  distributionChartInstance.value = echarts.init(distributionChart.value)
  
  const hours = timeDistributionData.value.map(item => item.hour)
  const counts = timeDistributionData.value.map(item => item.count)
  
  const option = {
    title: {
      text: '时段客流分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
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
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }
  
  distributionChartInstance.value.setOption(option)
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

const handleExport = async (format) => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请先选择时间范围')
    return
  }
  
  try {
    const [startDate, endDate] = dateRange.value
    const response = await customerFlowApi.exportReport(
      startDate,
      endDate,
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
    link.download = `footfall_report_${startDate}_${endDate}.${format === 'pdf' ? 'pdf' : 'csv'}`
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
    if (trendChartInstance.value) {
      trendChartInstance.value.resize()
    }
    if (distributionChartInstance.value) {
      distributionChartInstance.value.resize()
    }
  })
})

// 监听数据变化，更新图表
watch([customerFlowData, timeDistributionData], () => {
  updateCharts()
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
</style>