<template>
  <div class="batch-import">
    <Card title="批量导入学生" :bordered="false">
      <Form :label-width="120">
        <FormItem label="下载模板">
          <Button type="primary" @click="downloadTemplate">
            <Icon type="ios-download" /> 下载CSV模板
          </Button>
          <span style="margin-left: 10px; color: #999;">
            模板包含：userName, name, gender, age, gradeName, collegeName
          </span>
        </FormItem>

        <FormItem label="上传文件">
          <Upload
            ref="upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleSuccess"
            :on-error="handleError"
            :format="['csv']"
            :max-size="2048"
            :on-format-error="handleFormatError"
            :on-exceeded-size="handleMaxSize"
          >
            <Button icon="ios-cloud-upload-outline">选择CSV文件</Button>
          </Upload>
          <div style="margin-top: 10px; color: #999;">
            仅支持CSV格式，最大2MB
          </div>
        </FormItem>

        <FormItem v-if="importResult" label="导入结果">
          <Alert :type="importResult.errorCount > 0 ? 'warning' : 'success'" show-icon>
            <template #title>
              导入完成: 成功 {{ importResult.successCount }} 条,
              失败 {{ importResult.errorCount }} 条
            </template>
            <div v-if="importResult.errors && importResult.errors.length > 0">
              <div style="margin-top: 10px;">
                <strong>错误详情:</strong>
                <ul style="margin-top: 5px; padding-left: 20px;">
                  <li v-for="(error, index) in importResult.errors" :key="index">
                    {{ error }}
                  </li>
                </ul>
              </div>
            </div>
          </Alert>
        </FormItem>
      </Form>
    </Card>
  </div>
</template>

<script>
import { downloadTemplate } from '@/api'

export default {
  name: 'BatchImportStudents',
  data() {
    return {
      uploadUrl: '/api/students/import/',
      uploadHeaders: {},
      importResult: null,
      uploading: false
    }
  },
  created() {
    // 设置上传请求头
    const token = localStorage.getItem('token')
    if (token) {
      this.uploadHeaders = {
        'Authorization': `Bearer ${token}`
      }
    }
  },
  methods: {
    downloadTemplate() {
      // 下载CSV模板
      window.location.href = '/api/students/export/template/'
      this.$Message.success('模板下载成功')
    },
    handleSuccess(response, file, fileList) {
      // 处理上传成功
      if (response.code === 0) {
        this.importResult = {
          successCount: response.data.success,
          errorCount: response.data.error,
          errors: response.data.errors
        }
        this.$Message.success('导入完成')
        // 刷新学生列表
        this.$emit('import-complete')
      } else {
        this.$Message.error(response.msg || '导入失败')
      }
    },
    handleError(error, file, fileList) {
      // 处理上传错误
      this.$Message.error('上传失败: ' + error.message)
    },
    handleFormatError(file, fileList) {
      this.$Message.error('文件格式错误，仅支持CSV格式')
    },
    handleMaxSize(file, fileList) {
      this.$Message.error('文件大小超过2MB限制')
    }
  }
}
</script>

<style scoped>
.batch-import {
  padding: 20px;
}
</style>
