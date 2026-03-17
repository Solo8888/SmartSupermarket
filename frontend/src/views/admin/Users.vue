<template>
  <div class="users-container">
    <h2>用户管理</h2>
    
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>手机号</th>
            <th>性别</th>
            <th>角色</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.phone || '-' }}</td>
            <td>{{ user.gender || '-' }}</td>
            <td>
              <select 
                v-model="user.role" 
                @change="handleRoleChange(user.id, user.role)"
                :disabled="user.role === 'system_admin'"
                class="form-select"
              >
                <option value="customer">普通用户</option>
                <option value="operations_manager">运营管理员</option>
                <option value="inventory_manager">库存管理员</option>
                <option value="system_admin">系统管理员</option>
              </select>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import userApi from '@/api/user'

export default {
  name: 'Users',
  data() {
    return {
      users: []
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      try {
        const response = await userApi.getUserList()
        this.users = response.items
      } catch (error) {
        this.$message.error('获取用户列表失败')
      }
    },
    async handleRoleChange(userId, role) {
      try {
        await userApi.updateUserRole(userId, role)
        this.$message.success('角色更新成功')
      } catch (error) {
        this.$message.error('角色更新失败')
        // 恢复原来的角色
        this.loadUsers()
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
.users-container {
  padding: 20px;
}

table {
  margin-top: 20px;
}

select {
  width: 150px;
}
</style>