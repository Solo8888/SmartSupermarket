<template>
  <div class="user-stores-container">
    <h2>用户门店管理</h2>
    
    <!-- 分配门店给用户 -->
    <div class="card mb-4">
      <div class="card-header">
        分配门店给用户
      </div>
      <div class="card-body">
        <form @submit.prevent="handleAllocateStore">
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label for="userId" class="form-label">选择用户</label>
                <select 
                  id="userId" 
                  v-model="allocationForm.user_id" 
                  class="form-select"
                  required
                >
                  <option value="">请选择用户</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.username }} ({{ user.role }})
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-3">
                <label for="storeId" class="form-label">选择门店</label>
                <select 
                  id="storeId" 
                  v-model="allocationForm.store_id" 
                  class="form-select"
                  required
                >
                  <option value="">请选择门店</option>
                  <option v-for="store in stores" :key="store.id" :value="store.id">
                    {{ store.name }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">分配门店</button>
        </form>
      </div>
    </div>
    
    <!-- 查看用户的门店列表 -->
    <div class="card mb-4">
      <div class="card-header">
        用户的门店列表
      </div>
      <div class="card-body">
        <div class="mb-3">
          <label for="userSelect" class="form-label">选择用户</label>
          <select 
            id="userSelect" 
            v-model="selectedUserId" 
            class="form-select"
            @change="loadUserStores"
          >
            <option value="">请选择用户</option>
            <option v-for="user in allAdminUsers" :key="user.id" :value="user.id">
              {{ user.username }}
            </option>
          </select>
        </div>
        <div v-if="userStores.length > 0">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>门店ID</th>
                <th>门店名称</th>
                <th>分配时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="store in userStores" :key="store.id">
                <td>{{ store.store_id }}</td>
                <td>{{ store.store_name }}</td>
                <td>{{ formatDate(store.created_at) }}</td>
                <td>
                  <button 
                    class="btn btn-danger btn-sm"
                    @click="handleRemoveStore(store.id)"
                  >
                    取消分配
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="selectedUserId" class="text-center text-muted">
          该用户暂无分配的门店
        </div>
      </div>
    </div>
    
    <!-- 查看门店的管理员列表 -->
    <div class="card">
      <div class="card-header">
        门店的管理员列表
      </div>
      <div class="card-body">
        <div class="mb-3">
          <label for="storeSelect" class="form-label">选择门店</label>
          <select 
            id="storeSelect" 
            v-model="selectedStoreId" 
            class="form-select"
            @change="loadStoreUsers"
          >
            <option value="">请选择门店</option>
            <option v-for="store in stores" :key="store.id" :value="store.id">
              {{ store.name }}
            </option>
          </select>
        </div>
        <div v-if="storeUsers.length > 0">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>用户ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>分配时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in storeUsers" :key="user.id">
                <td>{{ user.user_id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.role }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <button 
                    class="btn btn-danger btn-sm"
                    @click="handleRemoveUser(user.id)"
                  >
                    取消分配
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="selectedStoreId" class="text-center text-muted">
          该门店暂无分配的管理员
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import userStoreApi from '@/api/userStore'
import userApi from '@/api/user'
import { getStores } from '@/api/store'

export default {
  name: 'UserStores',
  data() {
    return {
      users: [],
      allAdminUsers: [],
      stores: [],
      allocationForm: {
        user_id: '',
        store_id: ''
      },
      selectedUserId: '',
      selectedStoreId: '',
      userStores: [],
      storeUsers: []
    }
  },
  watch: {
    'allocationForm.store_id': {
      handler() {
        // 重置用户选择
        this.allocationForm.user_id = ''
      }
    }
  },
  mounted() {
    // 先加载门店，再加载用户，因为loadUsers需要使用门店列表
    this.loadStores().then(() => {
      this.loadUsers()
    })
  },
  methods: {
    async loadUsers() {
      try {
        const response = await userApi.getUserList()
        // 过滤掉顾客、系统管理员，只显示运营管理员和库存管理员
        const adminUsers = response.items.filter(user => 
          user.role !== 'customer' && user.role !== 'system_admin'
        )
        
        // 保存所有管理员用户（用于用户选择）
        this.allAdminUsers = adminUsers
        
        // 过滤掉所有已分配的用户（无论分配到哪个门店）
        try {
          // 遍历所有门店，获取所有已分配的用户
          const allAllocatedUserIds = new Set()
          for (const store of this.stores) {
            try {
              const allocatedUsers = await userStoreApi.getStoreUsers(store.id)
              allocatedUsers.forEach(user => allAllocatedUserIds.add(user.user_id))
            } catch (error) {
              console.error(`获取门店 ${store.name} 的已分配用户失败:`, error)
            }
          }
          // 只保留未分配的用户（用于分配功能）
          this.users = adminUsers.filter(user => !allAllocatedUserIds.has(user.id))
        } catch (error) {
          console.error('获取已分配用户失败:', error)
          // 如果获取已分配用户失败，至少显示所有管理员用户
          this.users = adminUsers
        }
      } catch (error) {
        ElMessage.error('获取用户列表失败')
      }
    },
    async loadStores() {
      try {
        const response = await getStores({ page: 1, size: 100 })
        this.stores = response.items
        return Promise.resolve()
      } catch (error) {
        ElMessage.error('获取门店列表失败')
        return Promise.reject(error)
      }
    },
    async handleAllocateStore() {
      try {
        const { store_id } = this.allocationForm
        await userStoreApi.createStoreAllocation(this.allocationForm)
        ElMessage.success('门店分配成功')
        // 重置表单
        this.allocationForm = {
          user_id: '',
          store_id: ''
        }
        // 刷新相关列表
        this.loadUsers() // 重新加载用户列表，更新分配列表
        if (this.selectedStoreId === store_id) {
          this.loadStoreUsers() // 刷新门店管理员列表
        }
      } catch (error) {
        ElMessage.error(error.message || '门店分配失败')
      }
    },
    async loadUserStores() {
      if (!this.selectedUserId) {
        this.userStores = []
        return
      }
      try {
        this.userStores = await userStoreApi.getUserStores(this.selectedUserId)
      } catch (error) {
        ElMessage.error(error.message || '获取用户门店列表失败')
      }
    },
    async loadStoreUsers() {
      if (!this.selectedStoreId) {
        this.storeUsers = []
        return
      }
      try {
        this.storeUsers = await userStoreApi.getStoreUsers(this.selectedStoreId)
      } catch (error) {
        ElMessage.error(error.message || '获取门店管理员列表失败')
      }
    },
    async handleRemoveStore(allocationId) {
      try {
        await userStoreApi.deleteStoreAllocation(allocationId)
        ElMessage.success('取消分配成功')
        this.loadUserStores() // 刷新用户门店列表
        this.loadUsers() // 重新加载用户列表，使已取消分配的管理员重新出现在分配列表中
      } catch (error) {
        ElMessage.error(error.message || '取消分配失败')
      }
    },
    async handleRemoveUser(allocationId) {
      try {
        await userStoreApi.deleteStoreAllocation(allocationId)
        ElMessage.success('取消分配成功')
        this.loadStoreUsers() // 刷新门店管理员列表
        this.loadUsers() // 重新加载用户列表，使已取消分配的管理员重新出现在分配列表中
      } catch (error) {
        ElMessage.error(error.message || '取消分配失败')
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.user-stores-container {
  padding: 20px;
}

.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 600;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.table {
  margin-top: 15px;
}
</style>