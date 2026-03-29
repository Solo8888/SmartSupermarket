<template>
  <div class="reports-container">
    <h2 class="page-title">运营报表</h2>
    
    <!-- 报表类型选择 -->
    <div class="report-type-selector">
      <el-radio-group v-model="activeReportType" @change="handleReportTypeChange">
        <el-radio-button label="recommendation_conversion">推荐转化率分析</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-panel">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        
        <el-form-item label="门店">
          <el-select v-model="filterForm.storeId" placeholder="选择门店">
            <el-option label="全部门店" value="" />
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-select v-model="filterForm.categoryId" placeholder="选择分类">
            <el-option label="全部分类" value="" />
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="fetchReportData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 报表数据 -->
    <div v-if="loading" class="loading-container">
      <el-loading v-loading="loading" element-loading-text="加载中..." />
    </div>
    
    <div v-else-if="reportData" class="report-content">
      <!-- 汇总指标 -->
      <div class="summary-metrics">
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-label">推荐展示次数</div>
            <div class="metric-value">{{ reportData.summary.impressions }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">点击次数</div>
            <div class="metric-value">{{ reportData.summary.clicks }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">加购次数</div>
            <div class="metric-value">{{ reportData.summary.add_to_carts }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">购买次数</div>
            <div class="metric-value">{{ reportData.summary.purchases }}</div>
          </div>
        </el-card>
        
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-label">点击率</div>
            <div class="metric-value">{{ reportData.summary.click_rate }}%</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">加购率</div>
            <div class="metric-value">{{ reportData.summary.cart_rate }}%</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">购买率</div>
            <div class="metric-value">{{ reportData.summary.purchase_rate }}%</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">转化率</div>
            <div class="metric-value">{{ reportData.summary.conversion_rate }}%</div>
          </div>
        </el-card>
      </div>
      
      <!-- 趋势图表 -->
      <div class="trend-chart">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>转化趋势</span>
              <el-select v-model="timeGranularity" size="small" @change="fetchReportData">
                <el-option label="按日" value="day" />
                <el-option label="按周" value="week" />
                <el-option label="按月" value="month" />
              </el-select>
            </div>
          </template>
          <div ref="chartContainer" class="chart-container"></div>
        </el-card>
      </div>
      
      <!-- 详细数据表格 -->
      <div class="details-table">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>详细数据</span>
              <el-button type="primary" @click="exportReport">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </template>
          <el-table :data="reportData.details" style="width: 100%">
            <el-table-column prop="recommendation_id" label="推荐ID" width="180" />
            <el-table-column prop="user_id" label="用户ID" width="180" />
            <el-table-column prop="product_id" label="商品ID" width="180" />
            <el-table-column prop="product_name" label="商品名称" />
            <el-table-column prop="store_id" label="门店ID" width="180" />
            <el-table-column prop="category_id" label="分类ID" width="180" />
            <el-table-column prop="recommended_at" label="推荐时间" width="200" />
            <el-table-column prop="clicked_at" label="点击时间" width="200" />
            <el-table-column prop="added_to_cart_at" label="加购时间" width="200" />
            <el-table-column prop="purchased_at" label="购买时间" width="200" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-if="reportData.details.length > 0"
            class="pagination"
            layout="total, sizes, prev, pager, next, jumper"
            :total="reportData.details.length"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-card>
      </div>
    </div>
    
    <div v-else class="no-data">
      <el-empty description="暂无数据" />
    </div>
    
    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出报表"
      width="500px"
    >
      <el-form :model="exportForm" label-width="80px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="csv">CSV</el-radio>
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="json">JSON</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleExport">确定导出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Download } from '@element-plus/icons-vue'
import { reportAPI } from '../../api'

export default {
  name: 'Reports',
  components: {
    Download
  },
  setup() {
    // 响应式数据
    const activeReportType = ref('recommendation_conversion')
    const filterForm = ref({
      dateRange: null,
      storeId: '',
      categoryId: ''
    })
    const timeGranularity = ref('day')
    const loading = ref(false)
    const reportData = ref(null)
    const stores = ref([])
    const categories = ref([])
    const chartContainer = ref(null)
    const chart = ref(null)
    const pageSize = ref(10)
    const currentPage = ref(1)
    const exportDialogVisible = ref(false)
    const exportForm = ref({
      format: 'csv'
    })
    
    // 方法
    const fetchReportData = async () => {
      loading.value = true
      try {
        const [startDate, endDate] = filterForm.value.dateRange || []
        const response = await reportAPI.getRecommendationConversion({
          start_date: startDate,
          end_date: endDate,
          store_id: filterForm.value.storeId,
          category_id: filterForm.value.categoryId,
          time_granularity: timeGranularity.value,
          include_details: true
        })
        reportData.value = response
        nextTick(() => {
          renderChart()
        })
      } catch (error) {
        console.error('获取报表数据失败:', error)
        ElMessage.error('获取报表数据失败')
      } finally {
        loading.value = false
      }
    }
    
    const renderChart = () => {
      if (!chartContainer.value || !reportData.value) return
      
      if (chart.value) {
        chart.value.dispose()
      }
      
      chart.value = echarts.init(chartContainer.value)
      
      const trends = reportData.value.trends
      const dates = trends.map(item => item.date)
      const clickRates = trends.map(item => item.metrics.click_rate)
      const cartRates = trends.map(item => item.metrics.cart_rate)
      const purchaseRates = trends.map(item => item.metrics.purchase_rate)
      const conversionRates = trends.map(item => item.metrics.conversion_rate)
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['点击率', '加购率', '购买率', '转化率']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: dates
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '点击率',
            type: 'line',
            data: clickRates,
            smooth: true
          },
          {
            name: '加购率',
            type: 'line',
            data: cartRates,
            smooth: true
          },
          {
            name: '购买率',
            type: 'line',
            data: purchaseRates,
            smooth: true
          },
          {
            name: '转化率',
            type: 'line',
            data: conversionRates,
            smooth: true
          }
        ]
      }
      
      chart.value.setOption(option)
      
      window.addEventListener('resize', () => {
        chart.value?.resize()
      })
    }
    
    const handleReportTypeChange = () => {
      reportData.value = null
      fetchReportData()
    }
    
    const handleDateRangeChange = () => {
      // 可以在这里添加防抖处理
    }
    
    const resetFilters = () => {
      filterForm.value = {
        dateRange: null,
        storeId: '',
        categoryId: ''
      }
      timeGranularity.value = 'day'
      reportData.value = null
    }
    
    const getStatusType = (status) => {
      const typeMap = {
        'impression': 'info',
        'click': 'primary',
        'add_to_cart': 'success',
        'purchase': 'warning'
      }
      return typeMap[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const textMap = {
        'impression': '展示',
        'click': '点击',
        'add_to_cart': '加购',
        'purchase': '购买'
      }
      return textMap[status] || status
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
    }
    
    const handleCurrentChange = (current) => {
      currentPage.value = current
    }
    
    const exportReport = () => {
      exportDialogVisible.value = true
    }
    
    const handleExport = async () => {
      loading.value = true
      try {
        const [startDate, endDate] = filterForm.value.dateRange || []
        const response = await reportAPI.exportReport({
          report_type: activeReportType.value,
          start_date: startDate,
          end_date: endDate,
          store_id: filterForm.value.storeId,
          category_id: filterForm.value.categoryId,
          format: exportForm.value.format
        })
        
        // 下载文件
        const link = document.createElement('a')
        link.href = response.file_url
        link.download = response.file_name
        link.click()
        
        ElMessage.success('报表导出成功')
        exportDialogVisible.value = false
      } catch (error) {
        console.error('导出报表失败:', error)
        ElMessage.error('导出报表失败')
      } finally {
        loading.value = false
      }
    }
    
    const fetchStores = async () => {
      try {
        // 这里应该调用获取门店列表的API
        // 暂时使用模拟数据
        stores.value = [
          { id: 'store_1', name: '门店1' },
          { id: 'store_2', name: '门店2' }
        ]
      } catch (error) {
        console.error('获取门店列表失败:', error)
      }
    }
    
    const fetchCategories = async () => {
      try {
        // 这里应该调用获取分类列表的API
        // 暂时使用模拟数据
        categories.value = [
          { id: 'category_1', name: '分类1' },
          { id: 'category_2', name: '分类2' }
        ]
      } catch (error) {
        console.error('获取分类列表失败:', error)
      }
    }
    
    // 生命周期
    onMounted(() => {
      fetchStores()
      fetchCategories()
      // 默认获取最近30天的数据
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - 30)
      filterForm.value.dateRange = [
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      ]
      fetchReportData()
    })
    
    return {
      activeReportType,
      filterForm,
      timeGranularity,
      loading,
      reportData,
      stores,
      categories,
      chartContainer,
      pageSize,
      currentPage,
      exportDialogVisible,
      exportForm,
      fetchReportData,
      handleReportTypeChange,
      handleDateRangeChange,
      resetFilters,
      getStatusType,
      getStatusText,
      handleSizeChange,
      handleCurrentChange,
      exportReport,
      handleExport
    }
  }
}
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.report-type-selector {
  margin-bottom: 20px;
}

.filter-panel {
  margin-bottom: 20px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.loading-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-metrics {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.metric-card {
  flex: 1;
  min-width: 300px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.trend-chart {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.details-table {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.no-data {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .summary-metrics {
    flex-direction: column;
  }
  
  .filter-form {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>