<template>
  <div class="user-profiles-container">
    <h2 class="page-title">用户画像分析</h2>
    
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>用户标签体系</span>
        </div>
      </template>
      <div class="tags-container">
        <div v-if="loading" class="loading-container">
          <el-loading v-loading="loading" element-loading-text="加载中..." />
        </div>
        <div v-else-if="userTags.length > 0" class="tags-cloud">
          <el-tag 
            v-for="tag in userTags" 
            :key="tag.tag_id"
            :size="getTagSize(tag.weight)"
            :type="getTagType(tag.weight)"
            effect="dark"
          >
            {{ tag.tag_name }} ({{ (tag.weight * 100).toFixed(0) }}%)
          </el-tag>
        </div>
        <div v-else class="no-data">
          <el-empty description="暂无标签数据" />
        </div>
      </div>
    </el-card>
    
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>用户群体分类</span>
        </div>
      </template>
      <div class="segments-container">
        <div v-if="loading" class="loading-container">
          <el-loading v-loading="loading" element-loading-text="加载中..." />
        </div>
        <div v-else-if="userSegments.length > 0" class="segments-list">
          <el-table :data="userSegments" style="width: 100%">
            <el-table-column prop="segment_id" label="群体ID" width="180" />
            <el-table-column prop="segment_name" label="群体名称" />
            <el-table-column prop="user_count" label="用户数量" width="180" />
            <el-table-column prop="characteristics" label="特征描述">
              <template #default="scope">
                <div class="characteristics">
                  <el-tag 
                    v-for="(char, index) in scope.row.characteristics" 
                    :key="index"
                    size="small"
                  >
                    {{ char }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="viewSegmentDetail(scope.row.segment_id)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="no-data">
          <el-empty description="暂无群体数据" />
        </div>
      </div>
    </el-card>
    
    <!-- 群体详情对话框 -->
    <el-dialog
      v-model="segmentDetailVisible"
      :title="segmentDetail?.segment_name || '群体详情'"
      width="800px"
    >
      <div v-if="segmentDetailLoading" class="loading-container">
        <el-loading v-loading="segmentDetailLoading" element-loading-text="加载中..." />
      </div>
      <div v-else-if="segmentDetail" class="segment-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2">
            <el-descriptions-item label="群体ID">{{ segmentDetail.segment_id }}</el-descriptions-item>
            <el-descriptions-item label="群体名称">{{ segmentDetail.segment_name }}</el-descriptions-item>
            <el-descriptions-item label="用户数量">{{ segmentDetail.user_count }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ segmentDetail.created_at }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-section">
          <h3>特征描述</h3>
          <div class="characteristics">
            <el-tag 
              v-for="(char, index) in segmentDetail.characteristics" 
              :key="index"
            >
              {{ char }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h3>标签分布</h3>
          <div class="tag-distribution">
            <el-tag 
              v-for="(tag, index) in segmentDetail.tag_distribution" 
              :key="index"
              :size="getTagSize(tag.weight)"
              :type="getTagType(tag.weight)"
              effect="dark"
            >
              {{ tag.tag_name }} ({{ (tag.weight * 100).toFixed(0) }}%)
            </el-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h3>行为分析</h3>
          <div class="behavior-analysis">
            <pre>{{ JSON.stringify(segmentDetail.behavior_analysis, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="segmentDetailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userProfileAPI } from '../../api'

export default {
  name: 'UserProfiles',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const userTags = ref([])
    const userSegments = ref([])
    const segmentDetailVisible = ref(false)
    const segmentDetailLoading = ref(false)
    const segmentDetail = ref(null)
    
    // 方法
    const fetchUserTags = async () => {
      loading.value = true
      try {
        const response = await userProfileAPI.getUserTags()
        userTags.value = response.tags
      } catch (error) {
        console.error('获取用户标签失败:', error)
        ElMessage.error('获取用户标签失败')
      } finally {
        loading.value = false
      }
    }
    
    const fetchUserSegments = async () => {
      loading.value = true
      try {
        const response = await userProfileAPI.getUserSegments()
        userSegments.value = response.segments
      } catch (error) {
        console.error('获取用户群体失败:', error)
        ElMessage.error('获取用户群体失败')
      } finally {
        loading.value = false
      }
    }
    
    const viewSegmentDetail = async (segmentId) => {
      segmentDetailLoading.value = true
      try {
        const response = await userProfileAPI.getSegmentDetail(segmentId)
        segmentDetail.value = response
        segmentDetailVisible.value = true
      } catch (error) {
        console.error('获取群体详情失败:', error)
        ElMessage.error('获取群体详情失败')
      } finally {
        segmentDetailLoading.value = false
      }
    }
    
    const getTagSize = (weight) => {
      if (weight > 0.8) return 'large'
      if (weight > 0.5) return 'medium'
      return 'small'
    }
    
    const getTagType = (weight) => {
      if (weight > 0.8) return 'danger'
      if (weight > 0.5) return 'warning'
      return 'info'
    }
    
    // 生命周期
    onMounted(() => {
      fetchUserTags()
      fetchUserSegments()
    })
    
    return {
      loading,
      userTags,
      userSegments,
      segmentDetailVisible,
      segmentDetailLoading,
      segmentDetail,
      fetchUserTags,
      fetchUserSegments,
      viewSegmentDetail,
      getTagSize,
      getTagType
    }
  }
}
</script>

<style scoped>
.user-profiles-container {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 20px 0;
}

.segments-list {
  padding: 10px 0;
}

.characteristics {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.no-data {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.segment-detail {
  padding: 10px 0;
}

.detail-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.tag-distribution {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.behavior-analysis {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.behavior-analysis pre {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .user-profiles-container {
    padding: 10px;
  }
  
  .tags-cloud {
    justify-content: center;
  }
}
</style>