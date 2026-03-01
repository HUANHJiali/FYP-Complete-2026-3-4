<template>
  <div class="admin-tasks">
    <div class="page-header">
      <h2>任务管理</h2>
      <Button type="primary" @click="showAddModal">创建任务</Button>
    </div>

    <div class="search-section">
      <Input 
        v-model="searchKeyword" 
        placeholder="请输入任务标题或描述" 
        style="width: 300px; margin-right: 16px;"
        @on-enter="handleSearch"
      />
      <Select 
        v-model="searchType" 
        placeholder="任务类型" 
        style="width: 150px; margin-right: 16px;"
        clearable
      >
        <Option value="practice">练习任务</Option>
        <Option value="exam">考试任务</Option>
        <Option value="project">项目任务</Option>
      </Select>
      <Select 
        v-model="searchProject" 
        placeholder="所属学科" 
        style="width: 150px; margin-right: 16px;"
        clearable
        filterable
      >
        <Option 
          v-for="project in projects" 
          :key="project.id" 
          :value="String(project.id)"
          :label="String(project.name)"
        >
          {{ project.name }}
        </Option>
      </Select>
      <Button type="primary" @click="handleSearch">搜索</Button>
      <Button @click="resetSearch" style="margin-left: 8px;">重置</Button>
    </div>

    <Table 
      :columns="columns" 
      :data="tasks" 
      :loading="loading"
      :pagination="pagination"
      @on-page-change="handlePageChange"
      @on-page-size-change="handlePageSizeChange"
    >
      <template #action="{ row }">
        <Button type="primary" size="small" @click="editTask(row)" style="margin-right: 8px;">编辑</Button>
        <Button type="success" size="small" @click="manageQuestions(row)" style="margin-right: 8px;">题目管理</Button>
        <Button type="error" size="small" @click="deleteTask(row)">删除</Button>
      </template>
    </Table>

    <!-- 添加/编辑任务模态框 -->
    <Modal 
      v-model="showModal" 
      :title="isEdit ? '编辑任务' : '创建任务'"
      width="800"
      @on-ok="handleSubmit"
      @on-cancel="handleCancel"
    >
      <Form ref="formRef" :model="formData" :rules="formRules" :label-width="100">
        <Row :gutter="16">
          <Col span="12">
            <FormItem label="任务标题" prop="title">
              <Input v-model="formData.title" placeholder="请输入任务标题" />
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="任务类型" prop="type">
              <Select v-model="formData.type" placeholder="请选择任务类型">
                <Option value="practice">练习任务</Option>
                <Option value="exam">考试任务</Option>
                <Option value="project">项目任务</Option>
              </Select>
            </FormItem>
          </Col>
        </Row>
        <Row :gutter="16">
          <Col span="12">
            <FormItem label="所属学科" prop="project">
              <Select v-model="formData.project" placeholder="请选择学科" filterable>
                <Option 
                  v-for="project in projects" 
                  :key="project.id" 
                  :value="String(project.id)"
                  :label="String(project.name)"
                >
                  {{ project.name }}
                </Option>
              </Select>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="适用年级" prop="grade">
              <Select v-model="formData.grade" placeholder="请选择年级" filterable>
                <Option 
                  v-for="grade in grades" 
                  :key="grade.id" 
                  :value="String(grade.id)"
                  :label="String(grade.name)"
                >
                  {{ grade.name }}
                </Option>
              </Select>
            </FormItem>
          </Col>
        </Row>
        <Row :gutter="16">
          <Col span="12">
            <FormItem label="截止时间" prop="deadline">
              <DatePicker 
                v-model="formData.deadline" 
                type="datetime" 
                placeholder="选择截止时间"
                style="width: 100%"
              />
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="任务分值" prop="score">
              <InputNumber v-model="formData.score" :min="1" :max="200" style="width: 100%" />
            </FormItem>
          </Col>
        </Row>
        <FormItem label="任务描述" prop="description">
          <Input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入任务描述" 
          />
        </FormItem>
        <FormItem label="是否启用" prop="isActive">
          <Switch v-model="formData.isActive" />
        </FormItem>
      </Form>
    </Modal>

    <!-- 删除确认模态框 -->
    <Modal v-model="showDeleteModal" title="确认删除" @on-ok="confirmDelete">
      <p>确定要删除任务 "{{ taskToDelete.title }}" 吗？此操作不可恢复。</p>
    </Modal>

    <!-- 题目管理弹窗 -->
    <Modal v-model="showQuestionsModal" :title="'任务题目 - ' + currentTaskTitle" width="800" :footer-hide="true">
      <Spin v-if="taskQuestionsLoading" fix />
      <div v-else-if="taskQuestions.length === 0" style="text-align:center;padding:32px;color:#999">该任务暂无题目</div>
      <Table v-else :columns="[
        { title: '序号', type: 'index', width: 60 },
        { title: '题目内容', key: 'name', minWidth: 200 },
        { title: '题型', key: 'type', width: 80, render: (h, p) => h('span', ['选择','填空','判断','编程'][p.row.type] || p.row.type) },
        { title: '分值', key: 'score', width: 80 }
      ]" :data="taskQuestions" />
    </Modal>
  </div>
</template>

<script>
import { getAdminTasks, addAdminTask, updateAdminTask, deleteAdminTask, getAllProjects, getAllGrades, getTaskQuestions } from '@/api'
import { formatDate } from '@/utils/date'

export default {
  name: 'AdminTasks',
  data() {
    return {
      loading: false,
      searchKeyword: '',
      searchType: '',
      searchProject: '',
      tasks: [],
      projects: [],
      grades: [],
      columns: [
        { title: 'ID', key: 'id', width: 80 },
        { title: '任务标题', key: 'title', minWidth: 200 },
        { title: '任务类型', key: 'type', width: 120,
          render: (h, params) => {
            const typeMap = {
              'practice': '练习任务',
              'exam': '考试任务',
              'project': '项目任务'
            }
            return h('Tag', {
              props: {
                color: params.row.type === 'practice' ? 'blue' : params.row.type === 'exam' ? 'green' : 'orange'
              }
            }, typeMap[params.row.type] || params.row.type)
          }
        },
        { title: '学科', key: 'projectName', width: 120 },
        { title: '年级', key: 'gradeName', width: 120 },
        { title: '截止时间', key: 'deadline', width: 150 },
        { title: '分值', key: 'score', width: 80 },
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
        { title: '操作', slot: 'action', width: 200, fixed: 'right' }
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
        title: '',
        description: '',
        type: 'practice',
        project: null,
        grade: null,
        deadline: null,
        score: 100,
        isActive: true
      },
      formRules: {
        title: [
          { required: true, message: '请输入任务标题', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择任务类型', trigger: 'change' }
        ],
        project: [
          { required: true, message: '请选择学科', trigger: 'change' }
        ],
        grade: [
          { required: true, message: '请选择年级', trigger: 'change' }
        ],
        deadline: [
          { required: true, message: '请选择截止时间', trigger: 'change' }
        ],
        score: [
          { required: true, message: '请输入任务分值', trigger: 'blur' }
        ]
      },
      showDeleteModal: false,
      taskToDelete: {},
      // 题目管理弹窗
      showQuestionsModal: false,
      currentTaskTitle: '',
      taskQuestions: [],
      taskQuestionsLoading: false
    }
  },
  mounted() {
    this.loadTasks()
    this.loadProjects()
    this.loadGrades()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        const response = await getAdminTasks({
          page: this.pagination.current,
          pageSize: this.pagination.pageSize,
          keyword: this.searchKeyword,
          type: this.searchType,
          project: this.searchProject
        })
        if (response.code === 0) {
          this.tasks = response.data.list
          this.pagination.total = response.data.total
        } else {
          this.$Message.error(response.msg || '加载任务列表失败')
        }
      } catch (error) {
        console.error('加载任务列表失败:', error)
        this.$Message.error('加载任务列表失败')
      } finally {
        this.loading = false
      }
    },

    async loadProjects() {
      try {
        const response = await getAllProjects()
        if (response.code === 0) {
          this.projects = response.data
        }
      } catch (error) {
        console.error('加载学科列表失败:', error)
      }
    },

    async loadGrades() {
      try {
        const response = await getAllGrades()
        if (response.code === 0) {
          this.grades = response.data
        }
      } catch (error) {
        console.error('加载年级列表失败:', error)
      }
    },

    handleSearch() {
      this.pagination.current = 1
      this.loadTasks()
    },

    resetSearch() {
      this.searchKeyword = ''
      this.searchType = ''
      this.searchProject = ''
      this.pagination.current = 1
      this.loadTasks()
    },

    handlePageChange(page) {
      this.pagination.current = page
      this.loadTasks()
    },

    handlePageSizeChange(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.current = 1
      this.loadTasks()
    },

    showAddModal() {
      this.isEdit = false
      this.formData = {
        title: '',
        description: '',
        type: 'practice',
        project: null,
        grade: null,
        deadline: null,
        score: 100,
        isActive: true
      }
      this.showModal = true
    },

    editTask(task) {
      this.isEdit = true
      this.formData = { ...task }
      this.showModal = true
    },

    manageQuestions(task) {
      this.currentTaskTitle = task.title
      this.taskQuestions = []
      this.showQuestionsModal = true
      this.taskQuestionsLoading = true
      getTaskQuestions(task.id).then(resp => {
        if (resp.code === 0 || resp.data) {
          this.taskQuestions = resp.data || []
        } else {
          this.$Message.error(resp.msg || '获取题目列表失败')
        }
      }).catch(() => {
        this.$Message.error('获取题目列表失败')
      }).finally(() => {
        this.taskQuestionsLoading = false
      })
    },

    async handleSubmit() {
      try {
        if (!this.formData.title || !String(this.formData.title).trim()) {
          this.$Message.warning('请输入任务标题')
          return
        }
        if (!this.formData.type) {
          this.$Message.warning('请选择任务类型')
          return
        }
        if (!this.formData.project) {
          this.$Message.warning('请选择学科')
          return
        }
        if (!this.formData.grade) {
          this.$Message.warning('请选择年级')
          return
        }
        if (!this.formData.deadline) {
          this.$Message.warning('请选择截止时间')
          return
        }
        if (!this.formData.score && this.formData.score !== 0) {
          this.$Message.warning('请输入任务分值')
          return
        }

        const payload = {
          ...this.formData,
          deadline: this.formData.deadline instanceof Date ? formatDate(this.formData.deadline) : this.formData.deadline
        }

        let response
        if (this.isEdit) {
          response = await updateAdminTask(payload)
        } else {
          response = await addAdminTask(payload)
        }

        if (response.code === 0) {
          this.$Message.success(this.isEdit ? '编辑成功' : '创建成功')
          this.showModal = false
          this.loadTasks()
        } else {
          this.$Message.error(response.msg || '操作失败')
        }
      } catch (error) {
        console.error('操作失败:', error)
        const msg = error?.msg || error?.response?.data?.msg || '操作失败'
        this.$Message.error(msg)
      }
    },

    handleCancel() {
      this.showModal = false
      this.$refs.formRef.resetFields()
    },

    deleteTask(task) {
      this.taskToDelete = task
      this.showDeleteModal = true
    },

    async confirmDelete() {
      try {
        const response = await deleteAdminTask(this.taskToDelete.id)
        if (response.code === 0) {
          this.$Message.success('删除成功')
          this.loadTasks()
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
.admin-tasks {
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

.ivu-btn-success {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-tasks {
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
