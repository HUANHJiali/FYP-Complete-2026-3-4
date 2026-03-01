<template>
  <div class="admin-logs">
    <div class="page-header">
      <h1>操作日志</h1>
      <Button type="primary" icon="ios-download-outline" @click="handleExport">导出日志</Button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <Input
          v-model="searchForm.userId"
          placeholder="用户ID"
          style="width: 120px; margin-right: 12px"
          clearable
        />
        <Input
          v-model="searchForm.userName"
          placeholder="用户姓名"
          style="width: 120px; margin-right: 12px"
          clearable
        />
        <Select
          v-model="searchForm.operationType"
          placeholder="操作类型"
          style="width: 120px; margin-right: 12px"
          clearable
        >
          <Option value="">全部类型</Option>
          <Option value="login">登录</Option>
          <Option value="logout">登出</Option>
          <Option value="create">创建</Option>
          <Option value="update">更新</Option>
          <Option value="delete">删除</Option>
          <Option value="submit">提交</Option>
          <Option value="query">查询</Option>
        </Select>
        <Select
          v-model="searchForm.moduleName"
          placeholder="模块名称"
          style="width: 120px; margin-right: 12px"
          clearable
        >
          <Option value="">全部模块</Option>
          <Option value="system">系统</Option>
          <Option value="user">用户</Option>
          <Option value="exam">考试</Option>
          <Option value="question">题目</Option>
          <Option value="student">学生</Option>
          <Option value="teacher">教师</Option>
          <Option value="grade">班级</Option>
          <Option value="project">科目</Option>
          <Option value="task">任务</Option>
          <Option value="practice">练习</Option>
        </Select>
        <Select
          v-model="searchForm.status"
          placeholder="操作状态"
          style="width: 120px; margin-right: 12px"
          clearable
        >
          <Option value="">全部状态</Option>
          <Option value="1">成功</Option>
          <Option value="0">失败</Option>
        </Select>
        <DatePicker
          v-model="searchForm.startDate"
          type="date"
          placeholder="开始日期"
          style="width: 140px; margin-right: 12px"
          clearable
        />
        <DatePicker
          v-model="searchForm.endDate"
          type="date"
          placeholder="结束日期"
          style="width: 140px; margin-right: 12px"
          clearable
        />
        <Button type="primary" @click="handleSearch">搜索</Button>
        <Button style="margin-left: 8px" @click="resetSearch">重置</Button>
        <Button
          v-if="selectedIds.length > 0"
          type="error"
          style="margin-left: 8px"
          @click="handleBatchDelete"
        >
          批量删除 ({{ selectedIds.length }})
        </Button>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="table-section">
      <Table
        :columns="columns"
        :data="logsList"
        :loading="loading"
        @on-selection-change="handleSelectionChange"
      >
        <template #status="{ row }">
          <Tag :color="row.status === 1 ? 'success' : 'error'">
            {{ row.status === 1 ? '成功' : '失败' }}
          </Tag>
        </template>
        <template #operationType="{ row }">
          <Tag color="primary">{{ row.operationTypeName || row.operationType }}</Tag>
        </template>
        <template #userType="{ row }">
          <Tag>{{ row.userTypeName || row.userType }}</Tag>
        </template>
        <template #action="{ row }">
          <Button type="primary" size="small" @click="showDetail(row)">详情</Button>
        </template>
      </Table>

      <!-- 分页 -->
      <div class="pagination-section">
        <Page
          :total="total"
          :current="pageIndex"
          :page-size="pageSize"
          @on-change="handlePageChange"
          show-elevator
          show-sizer
          @on-page-size-change="handlePageSizeChange"
        />
      </div>
    </div>

    <!-- 日志详情模态框 -->
    <Modal
      v-model="showDetailModal"
      title="操作日志详情"
      width="800"
      :footer-hide="true"
    >
      <div v-if="currentLog" class="log-detail">
        <Descriptions :column="2" border>
          <DescriptionsItem label="日志ID">{{ currentLog.id }}</DescriptionsItem>
          <DescriptionsItem label="操作状态">
            <Tag :color="currentLog.status === 1 ? 'success' : 'error'">
              {{ currentLog.status === 1 ? '成功' : '失败' }}
            </Tag>
          </DescriptionsItem>
          <DescriptionsItem label="用户ID">{{ currentLog.userId }}</DescriptionsItem>
          <DescriptionsItem label="用户姓名">{{ currentLog.userName }}</DescriptionsItem>
          <DescriptionsItem label="用户类型">
            <Tag>{{ currentLog.userTypeName }}</Tag>
          </DescriptionsItem>
          <DescriptionsItem label="操作类型">
            <Tag color="primary">{{ currentLog.operationTypeName }}</Tag>
          </DescriptionsItem>
          <DescriptionsItem label="模块名称">{{ currentLog.moduleName }}</DescriptionsItem>
          <DescriptionsItem label="资源ID">{{ currentLog.resourceId || '-' }}</DescriptionsItem>
          <DescriptionsItem label="资源名称">{{ currentLog.resourceName || '-' }}</DescriptionsItem>
          <DescriptionsItem label="IP地址">{{ currentLog.ipAddress || '-' }}</DescriptionsItem>
          <DescriptionsItem label="设备类型">{{ currentLog.deviceType || '-' }}</DescriptionsItem>
          <DescriptionsItem label="浏览器">{{ currentLog.browserType || '-' }}</DescriptionsItem>
          <DescriptionsItem label="操作系统">{{ currentLog.osType || '-' }}</DescriptionsItem>
          <DescriptionsItem label="地理位置">{{ currentLog.location || '-' }}</DescriptionsItem>
          <DescriptionsItem label="操作时间" :span="2">{{ currentLog.createdAt }}</DescriptionsItem>
          <DescriptionsItem label="操作详情" :span="2" v-if="currentLog.operationDetail">
            <pre style="max-height: 200px; overflow-y: auto; margin: 0;">{{ currentLog.operationDetail }}</pre>
          </DescriptionsItem>
          <DescriptionsItem label="错误信息" :span="2" v-if="currentLog.errorMessage">
            <Alert :type="'error'" show-icon>{{ currentLog.errorMessage }}</Alert>
          </DescriptionsItem>
        </Descriptions>
      </div>
    </Modal>
  </div>
</template>

<script>
import {
  getPageOperationLogs,
  deleteOperationLogs,
  exportOperationLogs
} from '@/api/index.js'
import { triggerBlobDownload } from '@/utils/fileDownload'

export default {
  name: 'AdminLogs',
  data() {
    return {
      loading: false,
      logsList: [],
      total: 0,
      pageIndex: 1,
      pageSize: 10,
      selectedIds: [],
      showDetailModal: false,
      currentLog: null,
      searchForm: {
        userId: '',
        userName: '',
        operationType: '',
        moduleName: '',
        status: '',
        startDate: '',
        endDate: ''
      },
      columns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {
          title: '日志ID',
          key: 'id',
          width: 80,
          align: 'center'
        },
        {
          title: '用户',
          key: 'userName',
          width: 100,
          align: 'center'
        },
        {
          title: '用户类型',
          slot: 'userType',
          width: 80,
          align: 'center'
        },
        {
          title: '操作类型',
          slot: 'operationType',
          width: 100,
          align: 'center'
        },
        {
          title: '模块',
          key: 'moduleName',
          width: 80,
          align: 'center'
        },
        {
          title: '资源名称',
          key: 'resourceName',
          minWidth: 120,
          ellipsis: true
        },
        {
          title: '状态',
          slot: 'status',
          width: 80,
          align: 'center'
        },
        {
          title: 'IP地址',
          key: 'ipAddress',
          width: 120,
          align: 'center'
        },
        {
          title: '设备',
          key: 'deviceType',
          width: 80,
          align: 'center'
        },
        {
          title: '浏览器',
          key: 'browserType',
          width: 90,
          align: 'center'
        },
        {
          title: '操作时间',
          key: 'createdAt',
          width: 160,
          align: 'center'
        },
        {
          title: '操作',
          slot: 'action',
          width: 80,
          align: 'center',
          fixed: 'right'
        }
      ]
    };
  },
  mounted() {
    this.fetchLogs();
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      try {
        const params = {
          pageIndex: this.pageIndex,
          pageSize: this.pageSize,
          ...this.searchForm
        };

        // 格式化日期
        if (this.searchForm.startDate) {
          params.startDate = this.formatDate(this.searchForm.startDate);
        }
        if (this.searchForm.endDate) {
          params.endDate = this.formatDate(this.searchForm.endDate);
        }

        const response = await getPageOperationLogs(params);

        if (response.code === 0) {
          this.logsList = response.data.list;
          this.total = response.data.total;
        } else {
          this.$Message.error(response.msg || '获取日志列表失败');
        }
      } catch (error) {
        console.error('获取日志列表失败:', error);
        this.$Message.error('获取日志列表失败');
      } finally {
        this.loading = false;
      }
    },
    handleSearch() {
      this.pageIndex = 1;
      this.fetchLogs();
    },
    resetSearch() {
      this.searchForm = {
        userId: '',
        userName: '',
        operationType: '',
        moduleName: '',
        status: '',
        startDate: '',
        endDate: ''
      };
      this.pageIndex = 1;
      this.fetchLogs();
    },
    handlePageChange(page) {
      this.pageIndex = page;
      this.fetchLogs();
    },
    handlePageSizeChange(pageSize) {
      this.pageSize = pageSize;
      this.pageIndex = 1;
      this.fetchLogs();
    },
    handleSelectionChange(selection) {
      this.selectedIds = selection.map(item => item.id);
    },
    showDetail(row) {
      this.currentLog = row;
      this.showDetailModal = true;
    },
    async handleBatchDelete() {
      if (this.selectedIds.length === 0) {
        this.$Message.warning('请选择要删除的日志');
        return;
      }

      this.$Modal.confirm({
        title: '确认删除',
        content: `确定要删除选中的 ${this.selectedIds.length} 条日志吗？`,
        onOk: async () => {
          try {
            const response = await deleteOperationLogs(this.selectedIds.join(','));

            if (response.code === 0) {
              this.$Message.success(response.msg || '删除成功');
              this.selectedIds = [];
              this.fetchLogs();
            } else {
              this.$Message.error(response.msg || '删除失败');
            }
          } catch (error) {
            console.error('删除日志失败:', error);
            this.$Message.error('删除日志失败');
          }
        }
      });
    },
    async handleExport() {
      try {
        const filters = { ...this.searchForm };

        // 格式化日期
        if (this.searchForm.startDate) {
          filters.startDate = this.formatDate(this.searchForm.startDate);
        }
        if (this.searchForm.endDate) {
          filters.endDate = this.formatDate(this.searchForm.endDate);
        }

        const response = await exportOperationLogs(filters);

        triggerBlobDownload(response.data, `operation_logs_${Date.now()}.csv`, 'text/csv;charset=utf-8;');

        this.$Message.success('导出成功');
      } catch (error) {
        console.error('导出日志失败:', error);
        this.$Message.error('导出日志失败');
      }
    },
    formatDate(date) {
      if (!date) return '';
      const d = new Date(date);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    }
  }
};
</script>

<style scoped>
.admin-logs {
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

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #fff;
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

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.search-form .ivu-input,
.search-form .ivu-select,
.search-form .ivu-date-picker {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.search-form .ivu-input:focus,
.search-form .ivu-select-focused,
.search-form .ivu-date-picker-focused {
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

/* 日志详情美化 */
.log-detail pre {
  background: linear-gradient(135deg, #fff8f0 0%, #fff 100%);
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
  border: 1px solid #fa8c16;
  font-family: 'Courier New', monospace;
  line-height: 1.6;
  color: #333;
}

/* 分页区域美化 */
.pagination-section {
  margin-top: 20px;
  text-align: right;
}

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
.ivu-date-picker {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ivu-input:focus,
.ivu-select-focused,
.ivu-date-picker-focused {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 140, 22, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-logs {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    padding: 20px;
  }

  .search-form {
    flex-direction: column;
    align-items: stretch;
  }

  .search-form .ivu-input,
  .search-form .ivu-select,
  .search-form .ivu-date-picker {
    width: 100%;
  }
}
</style>
