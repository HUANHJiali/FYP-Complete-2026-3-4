<template>
  <div class="admin-subjects">
    <div class="page-header">
      <h2>学科管理</h2>
      <Button type="primary" @click="showAddModal">创建学科</Button>
    </div>

    <div class="search-section">
      <Input 
        v-model="searchKeyword" 
        placeholder="请输入学科名称或描述" 
        style="width: 300px; margin-right: 16px;"
        @on-enter="handleSearch"
      />
      <Button type="primary" @click="handleSearch">搜索</Button>
      <Button @click="resetSearch" style="margin-left: 8px;">重置</Button>
    </div>

    <Table 
      :columns="columns" 
      :data="subjects" 
      :loading="loading"
      :pagination="pagination"
      @on-page-change="handlePageChange"
      @on-page-size-change="handlePageSizeChange"
    >
      <template #action="{ row }">
        <Button type="primary" size="small" @click="editSubject(row)" style="margin-right: 8px;">编辑</Button>
        <Button type="error" size="small" @click="deleteSubject(row)">删除</Button>
      </template>
    </Table>

    <!-- 添加/编辑学科模态框 -->
    <Modal 
      v-model="showModal" 
      :title="isEdit ? '编辑学科' : '创建学科'"
      @on-ok="handleSubmit"
      @on-cancel="handleCancel"
    >
      <Form ref="formRef" :model="formData" :rules="formRules" :label-width="80">
        <FormItem label="学科名称" prop="name">
          <Input v-model="formData.name" placeholder="请输入学科名称" />
        </FormItem>
        <FormItem label="学科描述" prop="description">
          <Input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入学科描述" 
          />
        </FormItem>
        <FormItem label="学科代码" prop="code">
          <Input v-model="formData.code" placeholder="请输入学科代码" />
        </FormItem>
        <FormItem label="是否启用" prop="isActive">
          <Switch v-model="formData.isActive" />
        </FormItem>
      </Form>
    </Modal>

    <!-- 删除确认模态框 -->
    <Modal v-model="showDeleteModal" title="确认删除" @on-ok="confirmDelete">
      <p>确定要删除学科 "{{ subjectToDelete.name }}" 吗？此操作不可恢复。</p>
    </Modal>
  </div>
</template>

<script>
import { getAdminSubjects, addAdminSubject, updateAdminSubject, deleteAdminSubject } from '@/api'

export default {
  name: 'AdminSubjects',
  data() {
    return {
      loading: false,
      searchKeyword: '',
      subjects: [],
      columns: [
        { title: 'ID', key: 'id', width: 80 },
        { title: '学科名称', key: 'name', minWidth: 150 },
        { title: '学科代码', key: 'code', width: 120 },
        { title: '学科描述', key: 'description', minWidth: 200 },
        { title: '状态', key: 'isActive', width: 100, 
          render: (h, params) => {
            return h('Tag', {
              props: {
                color: params.row.isActive ? 'success' : 'default'
              }
            }, params.row.isActive ? '启用' : '禁用')
          }
        },
        { title: '创建时间', key: 'createTime', width: 150 },
        { title: '操作', slot: 'action', width: 150, fixed: 'right' }
      ],
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
      },
      showModal: false,
      isEdit: false,
      formData: {
        name: '',
        description: '',
        code: '',
        isActive: true
      },
      formRules: {
        name: [
          { required: true, message: '请输入学科名称', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入学科代码', trigger: 'blur' }
        ]
      },
      showDeleteModal: false,
      subjectToDelete: {}
    }
  },
  mounted() {
    this.loadSubjects()
  },
  methods: {
    async loadSubjects() {
      this.loading = true
      try {
        const response = await getAdminSubjects({
          page: this.pagination.current,
          pageSize: this.pagination.pageSize,
          keyword: this.searchKeyword
        })
        if (response.code === 0) {
          this.subjects = response.data.list
          this.pagination.total = response.data.total
        } else {
          this.$Message.error(response.msg || '加载学科列表失败')
        }
      } catch (error) {
        console.error('加载学科列表失败:', error)
        this.$Message.error('加载学科列表失败')
      } finally {
        this.loading = false
      }
    },

    handleSearch() {
      this.pagination.current = 1
      this.loadSubjects()
    },

    resetSearch() {
      this.searchKeyword = ''
      this.pagination.current = 1
      this.loadSubjects()
    },

    handlePageChange(page) {
      this.pagination.current = page
      this.loadSubjects()
    },

    handlePageSizeChange(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.current = 1
      this.loadSubjects()
    },

    showAddModal() {
      this.isEdit = false
      this.formData = {
        name: '',
        description: '',
        code: '',
        isActive: true
      }
      this.showModal = true
    },

    editSubject(subject) {
      this.isEdit = true
      this.formData = { ...subject }
      this.showModal = true
    },

    async handleSubmit() {
      try {
        const valid = await this.$refs.formRef.validate()
        if (!valid) return

        let response
        if (this.isEdit) {
          response = await updateAdminSubject(this.formData)
        } else {
          response = await addAdminSubject(this.formData)
        }

        if (response.code === 0) {
          this.$Message.success(this.isEdit ? '编辑成功' : '创建成功')
          this.showModal = false
          this.loadSubjects()
        } else {
          this.$Message.error(response.msg || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        this.$Message.error('操作失败')
      }
    },

    handleCancel() {
      this.showModal = false
      this.$refs.formRef.resetFields()
    },

    deleteSubject(subject) {
      this.subjectToDelete = subject
      this.showDeleteModal = true
    },

    async confirmDelete() {
      try {
        const response = await deleteAdminSubject(this.subjectToDelete.id)
        if (response.code === 0) {
          this.$Message.success('删除成功')
          this.loadSubjects()
        } else {
          this.$Message.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除失败:', error)
        this.$Message.error('删除失败')
      } finally {
        this.showDeleteModal = false
      }
    }
  }
}
</script>

<style scoped>
.admin-subjects {
  padding: 24px;
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

.page-header h2 {
  margin: 0;
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

/* 搜索区域美化 */
.search-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.search-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.search-section .ivu-input,
.search-section .ivu-select {
  margin-right: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.search-section .ivu-input:focus,
.search-section .ivu-select-focused {
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

/* 表格美化 */
.ivu-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
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
.ivu-select {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-input:focus,
.ivu-select-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* Switch开关美化 */
.ivu-switch-checked {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-subjects {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
  }

  .search-section {
    padding: 16px;
  }

  .search-section .ivu-input,
  .search-section .ivu-select {
    width: 100%;
    margin-right: 0;
    margin-bottom: 12px;
  }
}
</style>
