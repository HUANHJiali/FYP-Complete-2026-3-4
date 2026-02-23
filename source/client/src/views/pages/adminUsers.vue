<template>
  <div class="admin-users">
    <div class="page-header">
      <h1>用户管理</h1>
      <Button type="primary" icon="ios-add" @click="showAddModal">添加用户</Button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <Input
          v-model="searchForm.search"
          placeholder="搜索用户名或姓名"
          style="width: 200px; margin-right: 16px"
          @on-enter="handleSearch"
        />
        <Select
          v-model="searchForm.type"
          placeholder="选择用户类型"
          style="width: 120px; margin-right: 16px"
          clearable
        >
          <Option value="">全部类型</Option>
          <Option value="0">管理员</Option>
          <Option value="1">教师</Option>
          <Option value="2">学生</Option>
        </Select>
        <Button type="primary" @click="handleSearch">搜索</Button>
        <Button style="margin-left: 8px" @click="resetSearch">重置</Button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-section">
      <Table
        :columns="columns"
        :data="usersList"
        :loading="loading"
        :pagination="pagination"
        @on-change="handlePageChange"
      >
        <template #action="{ row }">
          <Button type="primary" size="small" style="margin-right: 8px" @click="editUser(row)">
            编辑
          </Button>
          <Button type="error" size="small" @click="deleteUser(row)">删除</Button>
        </template>
      </Table>
    </div>

    <!-- 添加/编辑用户模态框 -->
    <Modal
      v-model="showModal"
      :title="modalTitle"
      width="600"
      @on-ok="handleSubmit"
      @on-cancel="resetForm"
    >
      <Form ref="userForm" :model="userForm" :rules="userRules" :label-width="100">
        <FormItem label="用户类型" prop="type">
          <Select v-model="userForm.type" placeholder="选择用户类型" @on-change="handleTypeChange">
            <Option value="0">管理员</Option>
            <Option value="1">教师</Option>
            <Option value="2">学生</Option>
          </Select>
        </FormItem>
        
        <FormItem label="用户名" prop="userName">
          <Input v-model="userForm.userName" placeholder="请输入用户名" />
        </FormItem>
        
        <FormItem label="密码" prop="passWord" v-if="!isEdit">
          <Input v-model="userForm.passWord" type="password" placeholder="请输入密码" />
        </FormItem>
        
        <FormItem label="真实姓名" prop="name">
          <Input v-model="userForm.name" placeholder="请输入真实姓名" />
        </FormItem>
        
        <FormItem label="性别" prop="gender">
          <RadioGroup v-model="userForm.gender">
            <Radio label="男">男</Radio>
            <Radio label="女">女</Radio>
          </RadioGroup>
        </FormItem>
        
        <FormItem label="年龄" prop="age">
          <InputNumber v-model="userForm.age" :min="1" :max="100" style="width: 100%" />
        </FormItem>

        <!-- 教师特有字段 -->
        <template v-if="userForm.type === '1'">
          <FormItem label="手机号" prop="phone">
            <Input v-model="userForm.phone" placeholder="请输入手机号" />
          </FormItem>
          <FormItem label="学历" prop="record">
            <Input v-model="userForm.record" placeholder="请输入学历" />
          </FormItem>
          <FormItem label="职位" prop="job">
            <Input v-model="userForm.job" placeholder="请输入职位" />
          </FormItem>
        </template>

        <!-- 学生特有字段 -->
        <template v-if="userForm.type === '2'">
          <FormItem label="年级" prop="gradeId">
            <Select v-model="userForm.gradeId" placeholder="选择年级" clearable>
              <Option
                v-for="grade in gradesList"
                :key="grade.id"
                :value="grade.id"
                :label="grade.name"
              />
            </Select>
          </FormItem>
          <FormItem label="学院" prop="collegeId">
            <Select v-model="userForm.collegeId" placeholder="选择学院" clearable>
              <Option
                v-for="college in collegesList"
                :key="college.id"
                :value="college.id"
                :label="college.name"
              />
            </Select>
          </FormItem>
        </template>
      </Form>
    </Modal>
  </div>
</template>

<script>
import {
  getAdminUsers,
  addAdminUser,
  updateAdminUser,
  deleteAdminUser,
  getAllGrades,
  getAllColleges
} from '@/api/index.js'

export default {
  name: 'AdminUsers',
  data() {
    return {
      loading: false,
      usersList: [],
      gradesList: [],
      collegesList: [],
      searchForm: {
        search: '',
        type: ''
      },
      userForm: {
        type: '',
        userName: '',
        passWord: '',
        name: '',
        gender: '男',
        age: 18,
        phone: '',
        record: '',
        job: '',
        gradeId: '',
        collegeId: ''
      },
      userRules: {
        type: [{ required: true, message: '请选择用户类型', trigger: 'change' }],
        userName: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        passWord: [{ required: true, message: '请输入密码', trigger: 'blur' }],
        name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
        gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
        age: [{ required: true, message: '请输入年龄', trigger: 'blur' }]
      },
      showModal: false,
      isEdit: false,
      currentUserId: null,
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
      }
    }
  },
  computed: {
    modalTitle() {
      return this.isEdit ? '编辑用户' : '添加用户'
    }
  },
  methods: {
    async loadUsers() {
      try {
        this.loading = true
        const params = {
          page: this.pagination.current,
          size: this.pagination.pageSize,
          search: this.searchForm.search,
          type: this.searchForm.type
        }
        
        const response = await getAdminUsers(params)
        if (response.code === 0) {
          this.usersList = response.data.list
          this.pagination.total = response.data.total
        } else {
          this.$Message.error(response.msg || '获取用户列表失败')
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        this.$Message.error('获取用户列表失败')
      } finally {
        this.loading = false
      }
    },

    async loadGrades() {
      try {
        const response = await getAllGrades()
        if (response.code === 0) {
          this.gradesList = response.data
        }
      } catch (error) {
        console.error('获取年级列表失败:', error)
      }
    },

    async loadColleges() {
      try {
        const response = await getAllColleges()
        if (response.code === 0) {
          this.collegesList = response.data
        }
      } catch (error) {
        console.error('获取学院列表失败:', error)
      }
    },

    handleSearch() {
      this.pagination.current = 1
      this.loadUsers()
    },

    resetSearch() {
      this.searchForm = {
        search: '',
        type: ''
      }
      this.pagination.current = 1
      this.loadUsers()
    },

    handlePageChange(page) {
      this.pagination.current = page.current
      this.pagination.pageSize = page.pageSize
      this.loadUsers()
    },

    showAddModal() {
      this.isEdit = false
      this.currentUserId = null
      this.resetForm()
      this.showModal = true
    },

    editUser(user) {
      this.isEdit = true
      this.currentUserId = user.id
      this.userForm = {
        type: user.type.toString(),
        userName: user.userName,
        passWord: '',
        name: user.name,
        gender: user.gender,
        age: user.age,
        phone: user.phone || '',
        record: user.record || '',
        job: user.job || '',
        gradeId: user.gradeId || '',
        collegeId: user.collegeId || ''
      }
      this.showModal = true
    },

    async deleteUser(user) {
      this.$Modal.confirm({
        title: '确认删除',
        content: `确定要删除用户 "${user.name}" 吗？删除后无法恢复。`,
        onOk: async () => {
          try {
            const response = await deleteAdminUser(user.id)
            if (response.code === 0) {
              this.$Message.success('用户删除成功')
              this.loadUsers()
            } else {
              this.$Message.error(response.msg || '删除失败')
            }
          } catch (error) {
            console.error('删除用户失败:', error)
            this.$Message.error('删除用户失败')
          }
        }
      })
    },

    handleTypeChange() {
      // 清空类型相关字段
      this.userForm.phone = ''
      this.userForm.record = ''
      this.userForm.job = ''
      this.userForm.gradeId = ''
      this.userForm.collegeId = ''
    },

    async handleSubmit() {
      try {
        // iView的validate()返回Promise，验证失败时会reject
        await this.$refs.userForm.validate()

        const token = this.$store.state.token || sessionStorage.getItem('token')
        const params = {
          token,
          ...this.userForm
        }

        let response
        if (this.isEdit) {
          params.id = this.currentUserId
          response = await updateAdminUser(params)
        } else {
          response = await addAdminUser(params)
        }

        if (response.code === 0) {
          this.$Message.success(this.isEdit ? '用户更新成功' : '用户创建成功')
          this.showModal = false
          this.loadUsers()
        } else {
          this.$Message.error(response.msg || '操作失败')
        }
      } catch (error) {
        // validate()失败时会进入这里，无需额外处理
        console.error('提交用户信息失败:', error)
      }
    },

    resetForm() {
      this.userForm = {
        type: '',
        userName: '',
        passWord: '',
        name: '',
        gender: '男',
        age: 18,
        phone: '',
        record: '',
        job: '',
        gradeId: '',
        collegeId: ''
      }
      // 在nextTick中重置，确保表单已渲染
      this.$nextTick(() => {
        this.$refs.userForm?.resetFields()
      })
    }
  },

  mounted() {
    this.loadUsers()
    this.loadGrades()
    this.loadColleges()
  }
}
</script>

<script setup>
// 表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '用户名',
    key: 'userName',
    width: 120
  },
  {
    title: '姓名',
    key: 'name',
    width: 100
  },
  {
    title: '类型',
    key: 'type',
    width: 80,
    render: (h, params) => {
      const typeMap = {
        0: { text: '管理员', color: 'success' },
        1: { text: '教师', color: 'primary' },
        2: { text: '学生', color: 'warning' }
      }
      const type = typeMap[params.row.type]
      return h('Tag', { props: { color: type.color } }, type.text)
    }
  },
  {
    title: '性别',
    key: 'gender',
    width: 60
  },
  {
    title: '年龄',
    key: 'age',
    width: 60
  },
  {
    title: '创建时间',
    key: 'createTime',
    width: 150
  },
  {
    title: '最后登录',
    key: 'lastLoginTime',
    width: 150
  },
  {
    title: '操作',
    slot: 'action',
    width: 150,
    fixed: 'right'
  }
]
</script>

<style scoped>
.admin-users {
  padding: 24px;
  background: linear-gradient(135deg, #fff7f0 0%, #fff 100%);
  min-height: 100vh;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 页面头部 - 橙色渐变主题 */
.page-header {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  box-shadow: 0 10px 30px rgba(250, 140, 22, 0.3);
}

.page-header h1 {
  margin: 0;
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

/* 搜索区域美化 */
.search-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.search-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.search-form .ivu-input,
.search-form .ivu-select {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.search-form .ivu-input:focus,
.search-form .ivu-select-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 按钮美化 */
.ivu-btn-primary {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.3);
}

.ivu-btn-error {
  background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-btn-error:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
}

/* 表格区域美化 */
.table-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.table-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* 表格美化 */
.ivu-table {
  border-radius: 8px;
  overflow: hidden;
}

.ivu-table th {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: #fff;
  font-weight: 600;
}

.ivu-table td {
  transition: background-color 0.3s ease;
}

.ivu-table tr:hover td {
  background-color: rgba(250, 140, 22, 0.05) !important;
}

/* 分页美化 */
.ivu-page-item {
  border-radius: 6px;
  transition: all 0.3s ease;
}

.ivu-page-item:hover {
  background: #fa8c16;
  color: #fff;
}

.ivu-page-item-active {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  border-color: #fa8c16;
}

/* 模态框美化 */
.ivu-modal-header {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
  color: #fff;
  border-radius: 12px 12px 0 0;
}

.ivu-modal-header-inner {
  color: #fff;
  font-weight: 600;
}

/* 表单美化 */
.ivu-form-item-label {
  font-weight: 500;
  color: #333;
}

.ivu-input,
.ivu-select,
.ivu-input-number {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-input:focus,
.ivu-select-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-users {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
  }

  .search-form {
    flex-wrap: wrap;
    gap: 12px;
  }

  .search-form .ivu-input,
  .search-form .ivu-select {
    width: 100%;
  }
}
</style>





