<script setup>
import { ref, onMounted, computed } from 'vue'
import { associationRulesApi } from '../../api/associationRules'
import * as echarts from 'echarts'

// 数据状态
const rules = ref([])
const loading = ref(false)
const chartLoading = ref(false)

// 查询参数
const queryParams = ref({
  start_date: '',
  end_date: '',
  min_support: 0.01,
  min_confidence: 0.5
})

// 图表实例
let supportChart = null
let confidenceChart = null
let scatterChart = null

// 初始化默认日期（最近30天）
const initDefaultDates = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  queryParams.value.end_date = end.toISOString().split('T')[0]
  queryParams.value.start_date = start.toISOString().split('T')[0]
}

// 获取关联规则数据
const fetchAssociationRules = async () => {
  loading.value = true
  chartLoading.value = true
  
  try {
    const response = await associationRulesApi.getAssociationRules({
      start_date: queryParams.value.start_date,
      end_date: queryParams.value.end_date,
      min_support: queryParams.value.min_support,
      min_confidence: queryParams.value.min_confidence
    })
    
    rules.value = response.rules || []
    
    // 更新图表
    updateCharts()
  } catch (err) {
    console.error('获取关联规则失败:', err)
    rules.value = []
  } finally {
    loading.value = false
    chartLoading.value = false
  }
}

// 计算统计数据
const stats = computed(() => {
  if (rules.value.length === 0) {
    return {
      totalRules: 0,
      avgSupport: 0,
      avgConfidence: 0,
      maxSupport: 0,
      maxConfidence: 0
    }
  }
  
  const totalRules = rules.value.length
  const avgSupport = rules.value.reduce((sum, r) => sum + r.support, 0) / totalRules
  const avgConfidence = rules.value.reduce((sum, r) => sum + r.confidence, 0) / totalRules
  const maxSupport = Math.max(...rules.value.map(r => r.support))
  const maxConfidence = Math.max(...rules.value.map(r => r.confidence))
  
  return {
    totalRules,
    avgSupport: avgSupport.toFixed(4),
    avgConfidence: avgConfidence.toFixed(4),
    maxSupport: maxSupport.toFixed(4),
    maxConfidence: maxConfidence.toFixed(4)
  }
})

// 格式化规则文本
const formatRule = (rule) => {
  const antecedent = rule.antecedent.join(' + ')
  const consequent = rule.consequent.join(' + ')
  return `${antecedent} → ${consequent}`
}

// 格式化百分比
const formatPercent = (value) => {
  return (value * 100).toFixed(2) + '%'
}

// 获取支持度颜色
const getSupportColor = (support) => {
  if (support >= 0.1) return '#10b981'
  if (support >= 0.05) return '#3b82f6'
  if (support >= 0.02) return '#f59e0b'
  return '#6b7280'
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#10b981'
  if (confidence >= 0.6) return '#3b82f6'
  if (confidence >= 0.5) return '#f59e0b'
  return '#ef4444'
}

// 初始化图表
const initCharts = () => {
  // 支持度分布图
  const supportChartDom = document.getElementById('support-chart')
  if (supportChartDom) {
    supportChart = echarts.init(supportChartDom)
  }
  
  // 置信度分布图
  const confidenceChartDom = document.getElementById('confidence-chart')
  if (confidenceChartDom) {
    confidenceChart = echarts.init(confidenceChartDom)
  }
  
  // 散点图
  const scatterChartDom = document.getElementById('scatter-chart')
  if (scatterChartDom) {
    scatterChart = echarts.init(scatterChartDom)
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateCharts = () => {
  if (!supportChart || !confidenceChart || !scatterChart) return
  
  // 支持度分布数据
  const supportRanges = {
    '0-2%': 0,
    '2-5%': 0,
    '5-10%': 0,
    '10%+': 0
  }
  
  // 置信度分布数据
  const confidenceRanges = {
    '50-60%': 0,
    '60-70%': 0,
    '70-80%': 0,
    '80%+': 0
  }
  
  rules.value.forEach(rule => {
    // 支持度分布
    if (rule.support < 0.02) supportRanges['0-2%']++
    else if (rule.support < 0.05) supportRanges['2-5%']++
    else if (rule.support < 0.1) supportRanges['5-10%']++
    else supportRanges['10%+']++
    
    // 置信度分布
    if (rule.confidence < 0.6) confidenceRanges['50-60%']++
    else if (rule.confidence < 0.7) confidenceRanges['60-70%']++
    else if (rule.confidence < 0.8) confidenceRanges['70-80%']++
    else confidenceRanges['80%+']++
  })
  
  // 支持度分布图配置
  const supportOption = {
    title: {
      text: '支持度分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Object.keys(supportRanges),
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: '规则数'
    },
    series: [{
      data: Object.values(supportRanges),
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#3b82f6' },
          { offset: 1, color: '#1d4ed8' }
        ])
      },
      barWidth: '60%'
    }]
  }
  
  // 置信度分布图配置
  const confidenceOption = {
    title: {
      text: '置信度分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Object.keys(confidenceRanges),
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: '规则数'
    },
    series: [{
      data: Object.values(confidenceRanges),
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#10b981' },
          { offset: 1, color: '#059669' }
        ])
      },
      barWidth: '60%'
    }]
  }
  
  // 散点图数据
  const scatterData = rules.value.map(rule => ({
    value: [rule.support, rule.confidence],
    name: formatRule(rule),
    rule: rule
  }))
  
  // 散点图配置
  const scatterOption = {
    title: {
      text: '支持度-置信度分布',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      formatter: function(params) {
        const rule = params.data.rule
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${formatRule(rule)}</div>
            <div>支持度: ${formatPercent(rule.support)}</div>
            <div>置信度: ${formatPercent(rule.confidence)}</div>
          </div>
        `
      }
    },
    grid: {
      left: '8%',
      right: '8%',
      bottom: '10%',
      top: '15%'
    },
    xAxis: {
      type: 'value',
      name: '支持度',
      nameLocation: 'middle',
      nameGap: 25,
      min: 0,
      max: Math.max(0.1, Math.max(...rules.value.map(r => r.support)) * 1.1),
      axisLabel: {
        formatter: value => (value * 100).toFixed(0) + '%'
      }
    },
    yAxis: {
      type: 'value',
      name: '置信度',
      nameLocation: 'middle',
      nameGap: 35,
      min: 0.5,
      max: 1,
      axisLabel: {
        formatter: value => (value * 100).toFixed(0) + '%'
      }
    },
    series: [{
      type: 'scatter',
      data: scatterData,
      symbolSize: 12,
      itemStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
          { offset: 0, color: '#60a5fa' },
          { offset: 1, color: '#2563eb' }
        ])
      }
    }]
  }
  
  supportChart.setOption(supportOption)
  confidenceChart.setOption(confidenceOption)
  scatterChart.setOption(scatterOption)
}

// 处理窗口大小变化
const handleResize = () => {
  supportChart?.resize()
  confidenceChart?.resize()
  scatterChart?.resize()
}

// 处理查询
const handleQuery = () => {
  if (!queryParams.value.start_date || !queryParams.value.end_date) {
    alert('请选择开始日期和结束日期')
    return
  }
  fetchAssociationRules()
}

// 重置查询
const handleReset = () => {
  initDefaultDates()
  queryParams.value.min_support = 0.01
  queryParams.value.min_confidence = 0.5
  fetchAssociationRules()
}

onMounted(() => {
  initDefaultDates()
  fetchAssociationRules()
  
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(() => {
    initCharts()
    updateCharts()
  }, 100)
})
</script>

<template>
  <div class="association-rules-page">
    <!-- 查询条件 -->
    <div class="query-card">
      <div class="query-form">
        <div class="form-row">
          <div class="form-group">
            <label>开始日期</label>
            <input 
              v-model="queryParams.start_date" 
              type="date" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>结束日期</label>
            <input 
              v-model="queryParams.end_date" 
              type="date" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>最小支持度</label>
            <input 
              v-model.number="queryParams.min_support" 
              type="number" 
              step="0.01"
              min="0"
              max="1"
              class="form-input"
              placeholder="0.01"
            />
          </div>
          <div class="form-group">
            <label>最小置信度</label>
            <input 
              v-model.number="queryParams.min_confidence" 
              type="number" 
              step="0.1"
              min="0"
              max="1"
              class="form-input"
              placeholder="0.5"
            />
          </div>
          <div class="form-group btn-group">
            <button class="btn btn-primary" @click="handleQuery">
              查询
            </button>
            <button class="btn btn-secondary" @click="handleReset">
              重置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalRules }}</div>
          <div class="stat-label">关联规则总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #dbeafe; color: #1d4ed8;">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercent(stats.avgSupport) }}</div>
          <div class="stat-label">平均支持度</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #d1fae5; color: #065f46;">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercent(stats.avgConfidence) }}</div>
          <div class="stat-label">平均置信度</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef3c7; color: #92400e;">⭐</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercent(stats.maxConfidence) }}</div>
          <div class="stat-label">最高置信度</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div id="support-chart" class="chart-container"></div>
        <div v-if="chartLoading" class="chart-loading">加载中...</div>
      </div>
      <div class="chart-card">
        <div id="confidence-chart" class="chart-container"></div>
        <div v-if="chartLoading" class="chart-loading">加载中...</div>
      </div>
    </div>

    <!-- 散点图 -->
    <div class="scatter-card">
      <div id="scatter-chart" class="scatter-container"></div>
      <div v-if="chartLoading" class="chart-loading">加载中...</div>
    </div>

    <!-- 规则列表 -->
    <div class="rules-card">
      <div class="card-header">
        <h3>关联规则列表</h3>
        <span class="rules-count">共 {{ rules.length }} 条规则</span>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="rules.length === 0" class="empty">
        暂无关联规则数据，请调整查询条件后重试
      </div>
      <div v-else class="rules-table-wrapper">
        <table class="rules-table">
          <thead>
            <tr>
              <th style="width: 50px;">序号</th>
              <th>关联规则</th>
              <th style="width: 120px;">支持度</th>
              <th style="width: 120px;">置信度</th>
              <th style="width: 100px;">提升度</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rule, index) in rules" :key="rule.rule_id">
              <td class="text-center">{{ index + 1 }}</td>
              <td>
                <div class="rule-text">
                  <span 
                    v-for="(item, idx) in rule.antecedent" 
                    :key="'ant-' + idx"
                    class="rule-item"
                  >
                    {{ item }}
                  </span>
                  <span class="rule-arrow">→</span>
                  <span 
                    v-for="(item, idx) in rule.consequent" 
                    :key="'cons-' + idx"
                    class="rule-item consequent"
                  >
                    {{ item }}
                  </span>
                </div>
              </td>
              <td>
                <div class="metric-cell">
                  <div class="metric-bar">
                    <div 
                      class="metric-fill" 
                      :style="{ 
                        width: formatPercent(rule.support),
                        backgroundColor: getSupportColor(rule.support)
                      }"
                    ></div>
                  </div>
                  <span class="metric-value">{{ formatPercent(rule.support) }}</span>
                </div>
              </td>
              <td>
                <div class="metric-cell">
                  <div class="metric-bar">
                    <div 
                      class="metric-fill" 
                      :style="{ 
                        width: formatPercent(rule.confidence),
                        backgroundColor: getConfidenceColor(rule.confidence)
                      }"
                    ></div>
                  </div>
                  <span class="metric-value">{{ formatPercent(rule.confidence) }}</span>
                </div>
              </td>
              <td class="text-center">
                <span class="lift-value">
                  {{ (rule.confidence / (rule.support || 1)).toFixed(2) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.association-rules-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 查询卡片 */
.query-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.query-form .form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  width: 140px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-group {
  flex-direction: row;
  gap: 8px;
}

.btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #eff6ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #9ca3af;
}

/* 散点图 */
.scatter-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
}

.scatter-container {
  width: 100%;
  height: 350px;
}

/* 规则列表 */
.rules-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.rules-count {
  font-size: 13px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 20px;
}

.loading,
.empty {
  padding: 60px 20px;
  text-align: center;
  color: #9ca3af;
}

.rules-table-wrapper {
  flex: 1;
  overflow: auto;
  padding: 0 24px 24px;
}

.rules-table {
  width: 100%;
  border-collapse: collapse;
}

.rules-table th,
.rules-table td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.rules-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.rules-table td {
  color: #4b5563;
  font-size: 14px;
}

.text-center {
  text-align: center;
}

/* 规则文本样式 */
.rule-text {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.rule-item {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.rule-item.consequent {
  background: #d1fae5;
  color: #065f46;
}

.rule-arrow {
  color: #9ca3af;
  font-weight: bold;
  padding: 0 4px;
}

/* 指标单元格 */
.metric-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  max-width: 80px;
}

.metric-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  min-width: 50px;
}

.lift-value {
  font-weight: 600;
  color: #7c3aed;
  background: #ede9fe;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .query-form .form-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-input {
    width: 100%;
  }
  
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .btn-group {
    justify-content: flex-end;
  }
  
  .rules-table-wrapper {
    padding: 0 16px 16px;
  }
  
  .rules-table th,
  .rules-table td {
    padding: 10px 8px;
    font-size: 12px;
  }
}
</style>
